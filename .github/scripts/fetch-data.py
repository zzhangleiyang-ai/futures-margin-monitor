import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "data.json"
LEGACY = ROOT / "data.json"

DEFAULT_PRODUCTS = [
    {"code": "AU", "name": "沪金", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 1000},
    {"code": "AG", "name": "沪银", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 15},
    {"code": "CU", "name": "沪铜", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "AL", "name": "沪铝", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "ZN", "name": "沪锌", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "PB", "name": "沪铅", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "NI", "name": "沪镍", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 1},
    {"code": "SN", "name": "沪锡", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 1},
    {"code": "RB", "name": "螺纹钢", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "HC", "name": "热卷", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "RU", "name": "橡胶", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "BU", "name": "沥青", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "FU", "name": "燃油", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "SP", "name": "纸浆", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 10},
    {"code": "SS", "name": "不锈钢", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "AO", "name": "氧化铝", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 20},
    {"code": "BR", "name": "合成橡胶", "exchange": "SHFE", "exchangeName": "上期所", "contractMultiplier": 5},
    {"code": "M", "name": "豆粕", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "Y", "name": "豆油", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "A", "name": "豆一", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "B", "name": "豆二", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "C", "name": "玉米", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "CS", "name": "淀粉", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "JD", "name": "鸡蛋", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "LH", "name": "生猪", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 16},
    {"code": "P", "name": "棕榈油", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "L", "name": "聚乙烯", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "PP", "name": "聚丙烯", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "V", "name": "聚氯乙烯", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "EG", "name": "乙二醇", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "EB", "name": "苯乙烯", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "J", "name": "焦炭", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 100},
    {"code": "JM", "name": "焦煤", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 60},
    {"code": "I", "name": "铁矿石", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 100},
    {"code": "RR", "name": "粳米", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 10},
    {"code": "BZ", "name": "纯苯", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 5},
    {"code": "PG", "name": "液化气", "exchange": "DCE", "exchangeName": "大商所", "contractMultiplier": 20},
    {"code": "SR", "name": "白糖", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 10},
    {"code": "CF", "name": "棉花", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "CY", "name": "棉纱", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "AP", "name": "苹果", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 10},
    {"code": "CJ", "name": "红枣", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "TA", "name": "PTA", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "MA", "name": "甲醇", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 10},
    {"code": "UR", "name": "尿素", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 20},
    {"code": "SA", "name": "纯碱", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 20},
    {"code": "FG", "name": "玻璃", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 20},
    {"code": "OI", "name": "菜油", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 10},
    {"code": "RM", "name": "菜粕", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 10},
    {"code": "PK", "name": "花生", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "SF", "name": "硅铁", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "SM", "name": "锰硅", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "PF", "name": "短纤", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "PX", "name": "对二甲苯", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 5},
    {"code": "SH", "name": "烧碱", "exchange": "CZCE", "exchangeName": "郑商所", "contractMultiplier": 30},
    {"code": "IF", "name": "沪深300", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 300},
    {"code": "IH", "name": "上证50", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 300},
    {"code": "IC", "name": "中证500", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 200},
    {"code": "IM", "name": "中证1000", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 200},
    {"code": "T", "name": "十年国债", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 10000},
    {"code": "TF", "name": "五年国债", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 10000},
    {"code": "TS", "name": "二年国债", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 20000},
    {"code": "TL", "name": "三十年国债", "exchange": "CFFEX", "exchangeName": "中金所", "contractMultiplier": 10000},
    {"code": "SC", "name": "原油", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 1000},
    {"code": "LU", "name": "低硫燃油", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 10},
    {"code": "NR", "name": "20号胶", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 10},
    {"code": "BC", "name": "国际铜", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 5},
    {"code": "EC", "name": "集运欧线", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 50},
    {"code": "LC", "name": "碳酸锂", "exchange": "GFEX", "exchangeName": "广期所", "contractMultiplier": 1},
    {"code": "PS", "name": "多晶硅", "exchange": "GFEX", "exchangeName": "广期所", "contractMultiplier": 3},
    {"code": "PT", "name": "铂", "exchange": "GFEX", "exchangeName": "广期所", "contractMultiplier": 1000},
    {"code": "SI", "name": "工业硅", "exchange": "GFEX", "exchangeName": "广期所", "contractMultiplier": 5},
]


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def tq_variety_code(product):
    code = product["code"]
    if product["exchange"] in {"SHFE", "DCE", "INE", "GFEX"}:
        return code.lower()
    return code.upper()


def read_previous_items():
    previous = {}
    for path in (OUT, LEGACY):
        if not path.exists():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = raw.get("items") if isinstance(raw, dict) else raw
        if not isinstance(rows, list):
            continue
        for row in rows:
            code = str(row.get("code") or row.get("c") or "").upper()
            if code:
                previous[code] = row
    return previous


def read_products():
    previous = read_previous_items()
    defaults = {item["code"]: item for item in DEFAULT_PRODUCTS}
    products = []
    for code in defaults:
        base = defaults[code]
        row = previous.get(code, {})
        products.append({
            "code": code,
            "name": row.get("name") or row.get("n") or base["name"],
            "exchange": base["exchange"],
            "exchangeName": base["exchangeName"],
            "contractMultiplier": base["contractMultiplier"],
        })
    return products


def fetch_with_tqsdk(products):
    user = os.environ.get("TQ_USER")
    password = os.environ.get("TQ_PASS")
    if not user or not password:
        raise RuntimeError("TQ_USER/TQ_PASS are not configured")

    from tqsdk import TqApi, TqAuth, TqSim

    api = TqApi(TqSim(), auth=TqAuth(user, password))
    main_quotes = {}
    exact_quotes = {}
    try:
        for product in products:
            symbol = f"KQ.m@{product['exchange']}.{tq_variety_code(product)}"
            main_quotes[product["code"]] = api.get_quote(symbol)

        for _ in range(20):
            api.wait_update(deadline=0.5)
            if sum(1 for q in main_quotes.values() if getattr(q, "underlying_symbol", "")) >= 20:
                break

        for code, quote in main_quotes.items():
            contract = getattr(quote, "underlying_symbol", "") or ""
            if contract:
                exact_quotes[code] = api.get_quote(contract)

        for _ in range(30):
            api.wait_update(deadline=0.5)
            if sum(1 for q in exact_quotes.values() if finite_number(getattr(q, "margin", None))) >= 20:
                break

        results = {}
        for code, main in main_quotes.items():
            exact = exact_quotes.get(code)
            if not exact:
                continue
            price = finite_number(getattr(main, "last_price", None)) or finite_number(getattr(exact, "last_price", None))
            pre_settlement = finite_number(getattr(exact, "pre_settlement", None))
            multiplier = finite_number(getattr(exact, "volume_multiple", None))
            margin = finite_number(getattr(exact, "margin", None))
            margin_rate = round(margin / (multiplier * pre_settlement), 4) if margin and multiplier and pre_settlement else None
            results[code] = {
                "price": price,
                "openInterest": int(getattr(main, "open_interest", 0) or getattr(exact, "open_interest", 0) or 0),
                "contract": getattr(exact, "instrument_id", "") or getattr(main, "underlying_symbol", "") or "",
                "contractMultiplier": int(multiplier) if multiplier and float(multiplier).is_integer() else multiplier,
                "marginRate": margin_rate,
                "marginPerLot": round(margin, 2) if margin else None,
                "marginSource": "TqSdk exact contract quote.margin",
                "preSettlement": pre_settlement,
            }
        return results
    finally:
        api.close()


def build_payload(status, products, latest, previous, message=""):
    items = []
    for product in products:
        code = product["code"]
        old = previous.get(code, {})
        quote = latest.get(code, {})
        price = finite_number(quote.get("price")) or finite_number(old.get("price", old.get("p")))
        multiplier = quote.get("contractMultiplier") or product.get("contractMultiplier") or old.get("contractMultiplier") or old.get("mul")
        margin_rate = finite_number(quote.get("marginRate")) or finite_number(old.get("marginRate", old.get("r")))
        margin_per_lot = finite_number(quote.get("marginPerLot"))
        if not margin_per_lot and price and multiplier and margin_rate:
            margin_per_lot = round(price * float(multiplier) * margin_rate, 2)

        items.append({
            "code": code,
            "name": product["name"],
            "exchange": product["exchange"],
            "exchangeName": product["exchangeName"],
            "price": price,
            "openInterest": int(quote.get("openInterest", old.get("openInterest", old.get("o", 0))) or 0),
            "contractMultiplier": multiplier,
            "marginRate": margin_rate,
            "marginPerLot": margin_per_lot,
            "contract": quote.get("contract") or old.get("contract", ""),
            "marginSource": quote.get("marginSource") or old.get("marginSource", "previous data"),
            "preSettlement": quote.get("preSettlement") or old.get("preSettlement"),
        })

    return {
        "status": status,
        "message": message,
        "updatedAt": now_iso(),
        "source": "TqSdk 主力连续合约定位实际主力合约；实际合约 quote.margin 反推当前保证金比例",
        "items": items,
    }


def main():
    products = read_products()
    previous = read_previous_items()
    status = "ok"
    message = ""
    try:
        latest = fetch_with_tqsdk(products)
        if not latest:
            raise RuntimeError("TqSdk returned no contract margin data")
    except Exception as exc:
        latest = {}
        status = "fallback"
        message = str(exc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload(status, products, latest, previous, message)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    priced = sum(1 for item in payload["items"] if item["price"])
    margins = sum(1 for item in payload["items"] if item["marginRate"])
    print(f"wrote {OUT} with {priced}/{len(payload['items'])} prices and {margins}/{len(payload['items'])} margin rates ({status})")


if __name__ == "__main__":
    main()
