import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "data.json"
LEGACY = ROOT / "data.json"


PRODUCTS = [
    {"code": "AU", "name": "沪金", "exchange": "SHFE", "exchangeName": "上期所", "tq": "au", "multiplier": 1000, "marginRate": 0.08},
    {"code": "AG", "name": "沪银", "exchange": "SHFE", "exchangeName": "上期所", "tq": "ag", "multiplier": 15, "marginRate": 0.09},
    {"code": "CU", "name": "沪铜", "exchange": "SHFE", "exchangeName": "上期所", "tq": "cu", "multiplier": 5, "marginRate": 0.08},
    {"code": "AL", "name": "沪铝", "exchange": "SHFE", "exchangeName": "上期所", "tq": "al", "multiplier": 5, "marginRate": 0.08},
    {"code": "ZN", "name": "沪锌", "exchange": "SHFE", "exchangeName": "上期所", "tq": "zn", "multiplier": 5, "marginRate": 0.08},
    {"code": "PB", "name": "沪铅", "exchange": "SHFE", "exchangeName": "上期所", "tq": "pb", "multiplier": 5, "marginRate": 0.08},
    {"code": "NI", "name": "沪镍", "exchange": "SHFE", "exchangeName": "上期所", "tq": "ni", "multiplier": 1, "marginRate": 0.10},
    {"code": "SN", "name": "沪锡", "exchange": "SHFE", "exchangeName": "上期所", "tq": "sn", "multiplier": 1, "marginRate": 0.10},
    {"code": "RB", "name": "螺纹钢", "exchange": "SHFE", "exchangeName": "上期所", "tq": "rb", "multiplier": 10, "marginRate": 0.07},
    {"code": "HC", "name": "热卷", "exchange": "SHFE", "exchangeName": "上期所", "tq": "hc", "multiplier": 10, "marginRate": 0.07},
    {"code": "RU", "name": "橡胶", "exchange": "SHFE", "exchangeName": "上期所", "tq": "ru", "multiplier": 10, "marginRate": 0.08},
    {"code": "BU", "name": "沥青", "exchange": "SHFE", "exchangeName": "上期所", "tq": "bu", "multiplier": 10, "marginRate": 0.10},
    {"code": "FU", "name": "燃油", "exchange": "SHFE", "exchangeName": "上期所", "tq": "fu", "multiplier": 10, "marginRate": 0.10},
    {"code": "SP", "name": "纸浆", "exchange": "SHFE", "exchangeName": "上期所", "tq": "sp", "multiplier": 10, "marginRate": 0.08},
    {"code": "SS", "name": "不锈钢", "exchange": "SHFE", "exchangeName": "上期所", "tq": "ss", "multiplier": 5, "marginRate": 0.10},
    {"code": "AO", "name": "氧化铝", "exchange": "SHFE", "exchangeName": "上期所", "tq": "ao", "multiplier": 20, "marginRate": 0.09},
    {"code": "BR", "name": "合成橡胶", "exchange": "SHFE", "exchangeName": "上期所", "tq": "br", "multiplier": 5, "marginRate": 0.09},
    {"code": "M", "name": "豆粕", "exchange": "DCE", "exchangeName": "大商所", "tq": "m", "multiplier": 10, "marginRate": 0.07},
    {"code": "Y", "name": "豆油", "exchange": "DCE", "exchangeName": "大商所", "tq": "y", "multiplier": 10, "marginRate": 0.07},
    {"code": "A", "name": "豆一", "exchange": "DCE", "exchangeName": "大商所", "tq": "a", "multiplier": 10, "marginRate": 0.08},
    {"code": "B", "name": "豆二", "exchange": "DCE", "exchangeName": "大商所", "tq": "b", "multiplier": 10, "marginRate": 0.08},
    {"code": "C", "name": "玉米", "exchange": "DCE", "exchangeName": "大商所", "tq": "c", "multiplier": 10, "marginRate": 0.07},
    {"code": "CS", "name": "淀粉", "exchange": "DCE", "exchangeName": "大商所", "tq": "cs", "multiplier": 10, "marginRate": 0.07},
    {"code": "JD", "name": "鸡蛋", "exchange": "DCE", "exchangeName": "大商所", "tq": "jd", "multiplier": 5, "marginRate": 0.08},
    {"code": "LH", "name": "生猪", "exchange": "DCE", "exchangeName": "大商所", "tq": "lh", "multiplier": 16, "marginRate": 0.08},
    {"code": "P", "name": "棕榈油", "exchange": "DCE", "exchangeName": "大商所", "tq": "p", "multiplier": 10, "marginRate": 0.08},
    {"code": "L", "name": "聚乙烯", "exchange": "DCE", "exchangeName": "大商所", "tq": "l", "multiplier": 5, "marginRate": 0.07},
    {"code": "PP", "name": "聚丙烯", "exchange": "DCE", "exchangeName": "大商所", "tq": "pp", "multiplier": 5, "marginRate": 0.07},
    {"code": "V", "name": "聚氯乙烯", "exchange": "DCE", "exchangeName": "大商所", "tq": "v", "multiplier": 5, "marginRate": 0.07},
    {"code": "EG", "name": "乙二醇", "exchange": "DCE", "exchangeName": "大商所", "tq": "eg", "multiplier": 10, "marginRate": 0.08},
    {"code": "EB", "name": "苯乙烯", "exchange": "DCE", "exchangeName": "大商所", "tq": "eb", "multiplier": 5, "marginRate": 0.08},
    {"code": "J", "name": "焦炭", "exchange": "DCE", "exchangeName": "大商所", "tq": "j", "multiplier": 100, "marginRate": 0.11},
    {"code": "JM", "name": "焦煤", "exchange": "DCE", "exchangeName": "大商所", "tq": "jm", "multiplier": 60, "marginRate": 0.11},
    {"code": "I", "name": "铁矿石", "exchange": "DCE", "exchangeName": "大商所", "tq": "i", "multiplier": 100, "marginRate": 0.11},
    {"code": "PG", "name": "液化气", "exchange": "DCE", "exchangeName": "大商所", "tq": "pg", "multiplier": 20, "marginRate": 0.08},
    {"code": "SR", "name": "白糖", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "SR", "multiplier": 10, "marginRate": 0.07},
    {"code": "CF", "name": "棉花", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "CF", "multiplier": 5, "marginRate": 0.07},
    {"code": "CY", "name": "棉纱", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "CY", "multiplier": 5, "marginRate": 0.07},
    {"code": "AP", "name": "苹果", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "AP", "multiplier": 10, "marginRate": 0.08},
    {"code": "CJ", "name": "红枣", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "CJ", "multiplier": 5, "marginRate": 0.08},
    {"code": "TA", "name": "PTA", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "TA", "multiplier": 5, "marginRate": 0.07},
    {"code": "MA", "name": "甲醇", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "MA", "multiplier": 10, "marginRate": 0.08},
    {"code": "UR", "name": "尿素", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "UR", "multiplier": 20, "marginRate": 0.08},
    {"code": "SA", "name": "纯碱", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "SA", "multiplier": 20, "marginRate": 0.08},
    {"code": "FG", "name": "玻璃", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "FG", "multiplier": 20, "marginRate": 0.08},
    {"code": "OI", "name": "菜油", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "OI", "multiplier": 10, "marginRate": 0.08},
    {"code": "RM", "name": "菜粕", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "RM", "multiplier": 10, "marginRate": 0.07},
    {"code": "PK", "name": "花生", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "PK", "multiplier": 5, "marginRate": 0.08},
    {"code": "SF", "name": "硅铁", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "SF", "multiplier": 5, "marginRate": 0.10},
    {"code": "SM", "name": "锰硅", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "SM", "multiplier": 5, "marginRate": 0.10},
    {"code": "PF", "name": "短纤", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "PF", "multiplier": 5, "marginRate": 0.08},
    {"code": "PX", "name": "对二甲苯", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "PX", "multiplier": 5, "marginRate": 0.10},
    {"code": "SH", "name": "烧碱", "exchange": "CZCE", "exchangeName": "郑商所", "tq": "SH", "multiplier": 30, "marginRate": 0.10},
    {"code": "IF", "name": "沪深300", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "IF", "multiplier": 300, "marginRate": 0.12},
    {"code": "IH", "name": "上证50", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "IH", "multiplier": 300, "marginRate": 0.12},
    {"code": "IC", "name": "中证500", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "IC", "multiplier": 200, "marginRate": 0.12},
    {"code": "IM", "name": "中证1000", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "IM", "multiplier": 200, "marginRate": 0.12},
    {"code": "T", "name": "十年国债", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "T", "multiplier": 10000, "marginRate": 0.02},
    {"code": "TF", "name": "五年国债", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "TF", "multiplier": 10000, "marginRate": 0.012},
    {"code": "TS", "name": "二年国债", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "TS", "multiplier": 20000, "marginRate": 0.005},
    {"code": "TL", "name": "三十年国债", "exchange": "CFFEX", "exchangeName": "中金所", "tq": "TL", "multiplier": 10000, "marginRate": 0.035},
    {"code": "SC", "name": "原油", "exchange": "INE", "exchangeName": "能源中心", "tq": "sc", "multiplier": 1000, "marginRate": 0.10},
    {"code": "LU", "name": "低硫燃油", "exchange": "INE", "exchangeName": "能源中心", "tq": "lu", "multiplier": 10, "marginRate": 0.10},
    {"code": "NR", "name": "20号胶", "exchange": "INE", "exchangeName": "能源中心", "tq": "nr", "multiplier": 10, "marginRate": 0.08},
    {"code": "BC", "name": "国际铜", "exchange": "INE", "exchangeName": "能源中心", "tq": "bc", "multiplier": 5, "marginRate": 0.08},
    {"code": "EC", "name": "集运欧线", "exchange": "INE", "exchangeName": "能源中心", "tq": "ec", "multiplier": 50, "marginRate": 0.18},
    {"code": "LC", "name": "碳酸锂", "exchange": "GFEX", "exchangeName": "广期所", "tq": "lc", "multiplier": 1, "marginRate": 0.09},
    {"code": "SI", "name": "工业硅", "exchange": "GFEX", "exchangeName": "广期所", "tq": "si", "multiplier": 5, "marginRate": 0.09},
]


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def read_previous_prices():
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
            price = finite_number(row.get("price", row.get("p")))
            if code and price:
                previous[code] = {
                    "price": price,
                    "openInterest": int(row.get("openInterest", row.get("o", 0)) or 0),
                }
    return previous


def fetch_with_tqsdk():
    user = os.environ.get("TQ_USER")
    password = os.environ.get("TQ_PASS")
    if not user or not password:
        raise RuntimeError("TQ_USER/TQ_PASS are not configured")

    from tqsdk import TqApi, TqAuth

    api = TqApi(auth=TqAuth(user, password))
    quotes = {}
    try:
        for product in PRODUCTS:
            symbol = f"KQ.m@{product['exchange']}.{product['tq']}"
            quotes[product["code"]] = api.get_quote(symbol)

        for _ in range(30):
            api.wait_update(deadline=0.5)
            if sum(1 for q in quotes.values() if finite_number(q.last_price)) >= 20:
                break

        results = {}
        for code, quote in quotes.items():
            price = finite_number(quote.last_price)
            if not price:
                continue
            results[code] = {
                "price": price,
                "openInterest": int(quote.open_interest or 0),
                "contract": str(getattr(quote, "underlying_symbol", "") or getattr(quote, "instrument_id", "") or ""),
            }
        return results
    finally:
        api.close()


def build_payload(status, prices, message=""):
    items = []
    for product in PRODUCTS:
        quote = prices.get(product["code"], {})
        price = finite_number(quote.get("price"))
        margin_per_lot = round(price * product["multiplier"] * product["marginRate"], 2) if price else None
        items.append({
            "code": product["code"],
            "name": product["name"],
            "exchange": product["exchange"],
            "exchangeName": product["exchangeName"],
            "price": price,
            "openInterest": int(quote.get("openInterest", 0) or 0),
            "contractMultiplier": product["multiplier"],
            "marginRate": product["marginRate"],
            "marginPerLot": margin_per_lot,
            "contract": quote.get("contract", ""),
        })
    return {
        "status": status,
        "message": message,
        "updatedAt": now_iso(),
        "source": "TqSdk 主力连续合约 + 交易所标准保证金参数",
        "items": items,
    }


def main():
    status = "ok"
    message = ""
    try:
        prices = fetch_with_tqsdk()
        if not prices:
            raise RuntimeError("TqSdk returned no quotes")
    except Exception as exc:
        prices = read_previous_prices()
        status = "fallback"
        message = str(exc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload(status, prices, message)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    available = sum(1 for item in payload["items"] if item["price"])
    print(f"wrote {OUT} with {available}/{len(payload['items'])} priced varieties ({status})")


if __name__ == "__main__":
    main()
