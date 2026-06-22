"""Fetch real-time futures data from Sina Finance HTTP API + akshare.
Called by GitHub Actions every 5 minutes during trading hours."""
import json, sys, os, urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "data" / "data.json"

# Read current data
try:
    with open(OUT, "r", encoding="utf-8") as f:
        data = json.load(f)
except:
    try:
        with open(ROOT / "data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"items": []}

items = data.get("items", [])
if not items:
    print("No items found")
    sys.exit(0)

# Try akshare settlement data first (for margin rates, official prices)
try:
    import akshare as ak
    has_akshare = True
except ImportError:
    has_akshare = False

if has_akshare:
    try:
        # Get SHFE settlement data (margin rates + settlement prices)
        shfe = {}
        for _, row in ak.futures_settle_shfe(date=datetime.now().strftime("%Y%m%d")).iterrows():
            shfe[str(row["symbol"]).strip()] = row
        for item in items:
            ex = item.get("exchange", "")
            contract = item.get("contract", "")
            if ex in ("SHFE", "INE") and contract in shfe:
                row = shfe[contract]
                sp = float(str(row.get("settle_price", "0")).replace(",", ""))
                if sp > 0:
                    item["preSettlement"] = sp
                mr = row.get("spec_long_margin_ratio")
                if mr:
                    item["marginRate"] = float(mr) / 100 if float(mr) > 1 else float(mr)
    except Exception as e:
        print(f"akshare settlement error: {e}")

# Fetch real-time quotes from Sina HTTP API
contracts = [item.get("contract", "") for item in items if item.get("contract")]
url = "http://hq.sinajs.cn/list=" + ",".join(contracts)
req = urllib.request.Request(url, headers={
    "Referer": "http://finance.sina.com.cn",
    "User-Agent": "Mozilla/5.0"
})

updated = 0
try:
    resp = urllib.request.urlopen(req, timeout=20)
    raw = resp.read().decode("gbk")
    
    code_map = {}
    for item in items:
        c = item.get("contract", "")
        if c:
            code_map[c.upper()] = item
            code_map[c.lower()] = item
            code_map[c] = item
    
    for line in raw.strip().split(";"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        parts = line.split("=", 1)
        var_name = parts[0].strip()
        data_str = parts[1].strip().strip('"').strip(';').strip('"')
        if not data_str:
            continue
        
        contract_code = var_name.replace("hq_str_", "")
        item = code_map.get(contract_code)
        if not item:
            continue
        
        fields = data_str.split(",")
        if len(fields) < 11:
            continue
        
        try:
            price = float(fields[3])
            oi = int(float(fields[7]))
        except (ValueError, IndexError):
            continue
        
        if price <= 0:
            continue
        
        item["price"] = price
        item["openInterest"] = oi
        
        mult = item.get("contractMultiplier")
        rate = item.get("marginRate")
        if mult and rate:
            item["marginPerLot"] = round(price * float(mult) * float(rate), 2)
        
        updated += 1
except Exception as e:
    print(f"Sina HTTP error: {e}")

data["status"] = "sina_live" if updated > 0 else "no_update"
data["updatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
data["liveCount"] = updated

# Save
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Written: {updated}/{len(items)} live, status={data['status']}")