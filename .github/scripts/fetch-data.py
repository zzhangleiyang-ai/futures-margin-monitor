import json
from datetime import datetime
from pathlib import Path

import akshare as ak


ROOT = Path(__file__).resolve().parents[2]
DATA_PATHS = [
    ROOT / "data" / "data.json",
    ROOT / "data.json",
    ROOT / "docs" / "data.json",
]


def load_catalog():
    for path in DATA_PATHS:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = payload.get("items")
        if isinstance(items, list) and items:
            return items
    raise RuntimeError("No existing catalog found in data.json")


def num(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def choose_main_contract(rows):
    ranked = rows.copy()
    ranked["_oi"] = ranked["持仓量"].apply(lambda x: num(x) or 0)
    ranked["_vol"] = ranked["成交量"].apply(lambda x: num(x) or 0)
    ranked = ranked.sort_values(["_oi", "_vol"], ascending=[False, False])
    return ranked.iloc[0]


def fetch_latest_rows():
    frame = ak.futures_fees_info()
    if frame.empty:
        raise RuntimeError("AKShare futures_fees_info returned empty data")
    frame = frame.copy()
    frame["品种代码"] = frame["品种代码"].astype(str).str.upper()
    return frame


def build_items(catalog, frame):
    items = []
    updated_at = None

    for base in catalog:
        code = str(base.get("code") or "").upper()
        rows = frame[frame["品种代码"] == code]
        if rows.empty:
            items.append(base)
            continue

        row = choose_main_contract(rows)
        price = num(row.get("最新价")) or num(row.get("上日结算价")) or base.get("price")
        multiplier = num(row.get("合约乘数")) or base.get("contractMultiplier")
        margin_rate = num(row.get("做多保证金率")) or base.get("marginRate")
        margin_per_lot = num(row.get("做多1手保证金"))

        if not margin_per_lot and price and multiplier and margin_rate:
            margin_per_lot = round(price * float(multiplier) * float(margin_rate), 2)

        row_updated_at = str(row.get("更新时间") or "").strip()
        if row_updated_at and (updated_at is None or row_updated_at > updated_at):
            updated_at = row_updated_at

        items.append(
            {
                "code": code,
                "name": base.get("name"),
                "exchange": base.get("exchange"),
                "exchangeName": base.get("exchangeName"),
                "price": price,
                "openInterest": int(num(row.get("持仓量")) or 0),
                "contractMultiplier": int(multiplier) if multiplier and float(multiplier).is_integer() else multiplier,
                "marginRate": margin_rate,
                "marginPerLot": margin_per_lot,
                "contract": str(row.get("合约代码") or base.get("contract") or "").strip().lower(),
                "marginSource": "AKShare futures_fees_info",
                "preSettlement": num(row.get("上日结算价")) or base.get("preSettlement"),
                "priceUpdatedAt": row_updated_at,
            }
        )

    return items, updated_at


def build_payload(items, updated_at):
    iso_updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    if updated_at:
        try:
            iso_updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S").astimezone().isoformat(timespec="seconds")
        except ValueError:
            pass

    return {
        "status": "ok",
        "message": "",
        "updatedAt": iso_updated_at,
        "source": "AKShare futures_fees_info",
        "items": items,
    }


def write_payload(payload):
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    for path in DATA_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def main():
    catalog = load_catalog()
    frame = fetch_latest_rows()
    items, updated_at = build_items(catalog, frame)
    payload = build_payload(items, updated_at)
    write_payload(payload)

    priced = sum(1 for item in items if num(item.get("price")))
    margined = sum(1 for item in items if num(item.get("marginRate")))
    print(
        f"wrote {len(items)} items, priced={priced}, margins={margined}, updatedAt={payload['updatedAt']}"
    )


if __name__ == "__main__":
    main()
