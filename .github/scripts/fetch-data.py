import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import akshare as ak


ROOT = Path(__file__).resolve().parents[2]
DATA_PATHS = [
    ROOT / "data" / "data.json",
    ROOT / "data.json",
    ROOT / "docs" / "data.json",
]
PRIMARY_SOURCE = "AKShare futures_fees_info"
SETTLEMENT_SOURCES = {
    "SHFE": ak.futures_settle_shfe,
    "INE": ak.futures_settle_ine,
    "CZCE": ak.futures_settle_czce,
    "CFFEX": ak.futures_settle_cffex,
    "GFEX": ak.futures_settle_gfex,
}


def now_local():
    return datetime.now().astimezone()


def now_iso():
    return now_local().isoformat(timespec="seconds")


def num(value):
    try:
        result = float(str(value).replace(",", "").strip())
    except (AttributeError, TypeError, ValueError):
        return None
    return result if result > 0 else None


def normalize_code(value):
    return str(value or "").strip().upper()


def normalize_contract(value):
    return str(value or "").strip().lower()


def latest_item_timestamp(items):
    latest = None
    for item in items:
        value = str(item.get("priceUpdatedAt") or "").strip()
        if not value:
            continue
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").astimezone()
        except ValueError:
            continue
        if latest is None or parsed > latest:
            latest = parsed
    return latest.isoformat(timespec="seconds") if latest else None


def load_payload():
    for path in DATA_PATHS:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = payload.get("items")
        if isinstance(items, list) and items:
            return payload
    raise RuntimeError("No existing catalog found in data.json")


def choose_main_contract(rows):
    ranked = rows.copy()
    ranked["_oi"] = ranked["持仓量"].apply(lambda x: num(x) or 0)
    ranked["_vol"] = ranked["成交量"].apply(lambda x: num(x) or 0)
    ranked = ranked.sort_values(["_oi", "_vol"], ascending=[False, False])
    return ranked.iloc[0]


def fetch_fees_rows():
    frame = ak.futures_fees_info()
    if frame.empty:
        raise RuntimeError("AKShare futures_fees_info returned empty data")
    frame = frame.copy()
    frame["品种代码"] = frame["品种代码"].astype(str).str.upper()
    return frame


def recent_trade_dates(days=7):
    base = now_local().date()
    return [(base - timedelta(days=offset)).strftime("%Y%m%d") for offset in range(days)]


def fetch_settlement_rows():
    results = {}
    notes = []
    for exchange, func in SETTLEMENT_SOURCES.items():
        loaded = False
        last_error = None
        for date_text in recent_trade_dates():
            try:
                frame = func(date=date_text)
            except Exception as exc:
                last_error = exc
                continue
            if frame is None or frame.empty:
                continue
            for _, row in frame.iterrows():
                contract = normalize_contract(row.get("symbol"))
                if not contract:
                    continue
                results[contract] = {
                    "exchange": exchange,
                    "date": date_text,
                    "row": row,
                }
            notes.append(f"{exchange}:{date_text}")
            loaded = True
            break
        if not loaded and last_error is not None:
            notes.append(f"{exchange}:error")
    return results, notes


def fetch_sina_quotes(contracts):
    codes = [normalize_contract(code) for code in contracts if normalize_contract(code)]
    if not codes:
        return {}
    url = "http://hq.sinajs.cn/list=" + ",".join(codes)
    request = urllib.request.Request(
        url,
        headers={
            "Referer": "http://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read().decode("gbk", errors="ignore")

    quotes = {}
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        left, right = line.split("=", 1)
        contract = normalize_contract(left.replace("hq_str_", ""))
        payload = right.strip().strip('"').strip(";").strip('"')
        if not contract or not payload:
            continue
        fields = payload.split(",")
        if len(fields) < 8:
            continue
        price = num(fields[3])
        open_interest = num(fields[7])
        if not price:
            continue
        quotes[contract] = {
            "price": price,
            "openInterest": int(open_interest or 0),
        }
    return quotes


def apply_fees_row(item, row):
    price = num(row.get("最新价")) or num(row.get("上日结算价")) or num(item.get("price"))
    multiplier = num(row.get("合约乘数")) or num(item.get("contractMultiplier"))
    margin_rate = num(row.get("做多保证金率")) or num(item.get("marginRate"))
    margin_per_lot = num(row.get("做多1手保证金"))
    if not margin_per_lot and price and multiplier and margin_rate:
        margin_per_lot = round(price * multiplier * margin_rate, 2)

    item.update(
        {
            "price": price,
            "openInterest": int(num(row.get("持仓量")) or 0),
            "contractMultiplier": int(multiplier) if multiplier and float(multiplier).is_integer() else multiplier,
            "marginRate": margin_rate,
            "marginPerLot": margin_per_lot,
            "contract": normalize_contract(row.get("合约代码") or item.get("contract")),
            "marginSource": PRIMARY_SOURCE,
            "preSettlement": num(row.get("上日结算价")) or item.get("preSettlement"),
            "priceUpdatedAt": str(row.get("更新时间") or "").strip(),
        }
    )
    return str(row.get("更新时间") or "").strip()


def apply_settlement_row(item, settlement):
    row = settlement["row"]
    settle_price = num(row.get("settle_price")) or num(item.get("preSettlement"))
    margin_rate = None
    for field in ("spec_long_margin_ratio", "margin_ratio", "spec_buy_rate"):
        margin_rate = num(row.get(field))
        if margin_rate:
            if margin_rate > 1:
                margin_rate = margin_rate / 100
            break

    if settle_price:
        item["preSettlement"] = settle_price
        item["price"] = num(item.get("price")) or settle_price
    if margin_rate:
        item["marginRate"] = margin_rate
    item["marginSource"] = f"AKShare {settlement['exchange']} settlement"
    item["priceUpdatedAt"] = settlement["date"]


def apply_sina_quote(item, quote):
    price = quote.get("price")
    if price:
        item["price"] = price
    item["openInterest"] = int(quote.get("openInterest") or 0)
    multiplier = num(item.get("contractMultiplier"))
    margin_rate = num(item.get("marginRate"))
    if price and multiplier and margin_rate:
        item["marginPerLot"] = round(price * multiplier * margin_rate, 2)


def build_items(catalog, fees_frame, settlement_map, sina_quotes):
    items = []
    updated_at = None
    stats = {
        "fees": 0,
        "settlement": 0,
        "quotes": 0,
    }

    for base in catalog:
        item = dict(base)
        code = normalize_code(base.get("code"))
        contract = normalize_contract(base.get("contract"))

        fees_rows = None if fees_frame is None else fees_frame[fees_frame["品种代码"] == code]
        if fees_rows is not None and not fees_rows.empty:
            row_updated_at = apply_fees_row(item, choose_main_contract(fees_rows))
            stats["fees"] += 1
            if row_updated_at and (updated_at is None or row_updated_at > updated_at):
                updated_at = row_updated_at
            contract = normalize_contract(item.get("contract"))
        else:
            settlement = settlement_map.get(contract)
            if settlement:
                apply_settlement_row(item, settlement)
                stats["settlement"] += 1

        quote = sina_quotes.get(contract)
        if quote:
            apply_sina_quote(item, quote)
            stats["quotes"] += 1

        item["code"] = code
        items.append(item)

    return items, updated_at, stats


def build_payload(previous_payload, items, updated_at, message, source, updated_at_iso=None):
    base_updated_at = latest_item_timestamp(items) or previous_payload.get("updatedAt") or now_iso()
    payload = {
        "status": "ok",
        "message": message,
        "updatedAt": base_updated_at,
        "source": source,
        "items": items,
        "lastAttemptAt": now_iso(),
    }
    if updated_at:
        try:
            payload["updatedAt"] = (
                datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                .astimezone()
                .isoformat(timespec="seconds")
            )
        except ValueError:
            payload["updatedAt"] = previous_payload.get("updatedAt") or now_iso()
    elif updated_at_iso:
        payload["updatedAt"] = updated_at_iso
    return payload


def write_payload(payload):
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    for path in DATA_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def main():
    previous_payload = load_payload()
    catalog = previous_payload["items"]
    errors = []
    source_parts = []

    fees_frame = None
    try:
        fees_frame = fetch_fees_rows()
        source_parts.append(PRIMARY_SOURCE)
    except Exception as exc:
        errors.append(f"fees:{exc}")

    settlement_map = {}
    settlement_notes = []
    if fees_frame is None:
        try:
            settlement_map, settlement_notes = fetch_settlement_rows()
            if settlement_map:
                source_parts.append("AKShare settlements")
        except Exception as exc:
            errors.append(f"settlement:{exc}")

    sina_quotes = {}
    try:
        sina_quotes = fetch_sina_quotes(item.get("contract") for item in catalog)
        if sina_quotes:
            source_parts.append("Sina quotes")
    except Exception as exc:
        errors.append(f"sina:{exc}")

    items, updated_at, stats = build_items(catalog, fees_frame, settlement_map, sina_quotes)

    if stats["fees"] == 0 and stats["settlement"] == 0 and stats["quotes"] == 0:
        message = "using cached data after fetch error: " + "; ".join(errors or ["no source updated"])
        source = previous_payload.get("source") or "cached"
        payload = build_payload(previous_payload, catalog, None, message, source)
    else:
        details = [
            f"fees={stats['fees']}",
            f"settlement={stats['settlement']}",
            f"quotes={stats['quotes']}",
        ]
        if settlement_notes:
            details.append("settlementDates=" + ",".join(settlement_notes))
        if errors:
            details.append("fallback=" + " | ".join(errors))
        message = "; ".join(details)
        updated_at_iso = now_iso() if stats["quotes"] > 0 and not updated_at else None
        payload = build_payload(
            previous_payload,
            items,
            updated_at,
            message,
            " + ".join(source_parts) if source_parts else (previous_payload.get("source") or "cached"),
            updated_at_iso=updated_at_iso,
        )

    write_payload(payload)

    priced = sum(1 for item in payload["items"] if num(item.get("price")))
    margined = sum(1 for item in payload["items"] if num(item.get("marginRate")))
    print(
        f"wrote {len(payload['items'])} items, priced={priced}, margins={margined}, "
        f"updatedAt={payload['updatedAt']}, source={payload['source']!r}, message={payload['message']!r}"
    )


if __name__ == "__main__":
    main()
