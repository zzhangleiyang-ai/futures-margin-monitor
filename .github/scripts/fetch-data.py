import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "data.json"
CSV_OUT = ROOT / "data" / "data.csv"
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
    {"code": "EC", "name": "集运指数欧线期货", "exchange": "INE", "exchangeName": "能源中心", "contractMultiplier": 50},
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


def normalize_contract(contract):
    text = str(contract or "").strip()
    return text.upper()


def parse_source_timestamp(value):
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


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
    for code, base in defaults.items():
        row = previous.get(code, {})
        products.append({
            "code": code,
            "name": row.get("name") or row.get("n") or base["name"],
            "exchange": base["exchange"],
            "exchangeName": base["exchangeName"],
            "contractMultiplier": base["contractMultiplier"],
        })
    return products


def choose_main_row(rows):
    rows = rows.copy()
    rows["_hold"] = rows["持仓量"].apply(lambda x: finite_number(x) or 0)
    rows["_volume"] = rows["成交量"].apply(lambda x: finite_number(x) or 0)
    rows = rows.sort_values(["_hold", "_volume"], ascending=[False, False])
    return rows.iloc[0]


def fetch_with_akshare(products):
    import akshare as ak

    frame = ak.futures_fees_info()
    if frame.empty:
        raise RuntimeError("AKShare futures_fees_info returned no rows")

    frame = frame.copy()
    frame["品种代码"] = frame["品种代码"].astype(str).str.upper()
    results = {}
    latest_source_time = None

    for product in products:
        code = product["code"]
        rows = frame[frame["品种代码"] == code]
        if rows.empty:
            continue

        row = choose_main_row(rows)
        source_time = parse_source_timestamp(row.get("更新时间"))
        if source_time and (latest_source_time is None or source_time > latest_source_time):
            latest_source_time = source_time

        price = finite_number(row.get("最新价"))
        multiplier = finite_number(row.get("合约乘数")) or product["contractMultiplier"]
        margin_rate = finite_number(row.get("做多保证金率"))
        margin_per_lot = finite_number(row.get("做多1手保证金"))
        if not margin_per_lot and price and multiplier and margin_rate:
            margin_per_lot = round(price * multiplier * margin_rate, 2)

        results[code] = {
            "price": price,
            "openInterest": int(finite_number(row.get("持仓量")) or 0),
            "contract": normalize_contract(row.get("合约代码")),
            "contractMultiplier": int(multiplier) if multiplier and float(multiplier).is_integer() else multiplier,
            "marginRate": margin_rate,
            "marginPerLot": margin_per_lot,
            "marginSource": "AKShare futures_fees_info (openctp)",
            "preSettlement": finite_number(row.get("上日结算价")),
            "priceUpdatedAt": str(row.get("更新时间") or ""),
        }

    if not results:
        raise RuntimeError("AKShare futures_fees_info produced no matched products")
    return results, latest_source_time


def build_payload(status, products, latest, previous, message="", updated_at=None):
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
            "priceUpdatedAt": quote.get("priceUpdatedAt") or old.get("priceUpdatedAt", ""),
        })

    return {
        "status": status,
        "message": message,
        "updatedAt": updated_at or now_iso(),
        "source": "AKShare futures_fees_info / openctp 参考表，按持仓量最大合约选取当前主力并读取保证金比例",
        "items": items,
    }


CSV_COLUMNS = [
    ("code", "品种代码"),
    ("name", "品种名称"),
    ("exchange", "交易所代码"),
    ("exchangeName", "交易所"),
    ("contract", "主力合约"),
    ("marginRate", "保证金比例"),
    ("marginPerLot", "每手保证金_元"),
    ("price", "最新价"),
    ("preSettlement", "昨结算"),
    ("openInterest", "持仓量"),
    ("contractMultiplier", "合约乘数"),
    ("priceUpdatedAt", "价格时间"),
    ("marginSource", "保证金来源"),
]


def write_csv(payload):
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["数据状态", "数据更新时间", *[header for _, header in CSV_COLUMNS]])
        for item in payload["items"]:
            writer.writerow(
                [payload["status"], payload["updatedAt"], *[item.get(key) for key, _ in CSV_COLUMNS]]
            )


def main():
    products = read_products()
    previous = read_previous_items()
    status = "ok"
    message = ""
    updated_at = now_iso()
    try:
        latest, latest_source_time = fetch_with_akshare(products)
        if not latest:
            raise RuntimeError("AKShare returned no contract margin data")
        if latest_source_time:
            updated_at = latest_source_time.astimezone().isoformat(timespec="seconds")
    except Exception as exc:
        latest = {}
        status = "fallback"
        message = str(exc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload(status, products, latest, previous, message, updated_at)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(payload)

    priced = sum(1 for item in payload["items"] if item["price"])
    margins = sum(1 for item in payload["items"] if item["marginRate"])
    print(
        f"wrote {OUT} and {CSV_OUT} with "
        f"{priced}/{len(payload['items'])} prices and {margins}/{len(payload['items'])} margin rates ({status})"
    )


if __name__ == "__main__":
    main()
