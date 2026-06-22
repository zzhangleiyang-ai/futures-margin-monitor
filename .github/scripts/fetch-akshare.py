#!/usr/bin/env python3
"""Fetch live futures data using AKShare + Sina HTTP API."""
import json, sys, os, urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "data" / "data.json"

try: data = json.loads(open(OUT, encoding="utf-8").read())
except:
    try: data = json.loads(open(ROOT / "data.json", encoding="utf-8").read())
    except: data = {"items": []}

items = data.get("items", [])
if not items: print("No items"); sys.exit(0)

import akshare as ak
now = datetime.now().strftime("%Y%m%d")
try:
    settlement = {}
    for src in [ak.futures_settle_shfe, ak.futures_settle_ine, ak.futures_settle_czce, ak.futures_settle_gfex]:
        for _, row in src(date=now).iterrows():
            settlement[str(row["symbol"]).strip()] = row
    for item in items:
        row = settlement.get(item.get("contract", ""))
        if row is None: continue
        sp = str(row.get("settle_price", "0")).replace(",", "")
        if sp and float(sp) > 0:
            item["preSettlement"] = float(sp)
            item["price"] = float(sp)
        for field in ["spec_long_margin_ratio","margin_ratio","spec_buy_rate"]:
            if field in row.index and row[field]:
                item["marginRate"] = float(row[field])/100 if float(row[field])>1 else float(row[field])
                break
    print(f"AKShare settlement: OK")
except Exception as e:
    print(f"Settlement error: {e}")

url = "http://hq.sinajs.cn/list=" + ",".join([i.get("contract","") for i in items if i.get("contract")])
try:
    resp = urllib.request.urlopen(urllib.request.Request(url, headers={"Referer":"http://finance.sina.com.cn","User-Agent":"Mozilla/5.0"}))
    raw = resp.read().decode("gbk")
    updated = 0
    for line in raw.split(";"):
        if "=" not in line: continue
        parts = line.split("=", 1)
        cc = parts[0].strip().replace("hq_str_", "")
        ds = parts[1].strip().strip('"').strip(";").strip('"')
        if not ds: continue
        fields = ds.split(",")
        if len(fields) < 11: continue
        try: price = float(fields[3]); oi = int(float(fields[7]))
        except: continue
        if price <= 0: continue
        for item in items:
            c = item.get("contract", "")
            if c.upper() == cc.upper() or c.lower() == cc.lower():
                item["price"] = price
                item["openInterest"] = oi
                m = item.get("contractMultiplier")
                r = item.get("marginRate")
                if m and r: item["marginPerLot"] = round(price * float(m) * float(r), 2)
                updated += 1
                break
    print(f"Sina live: {updated}/{len(items)} updated")
except Exception as e:
    print(f"Sina error: {e}")

data["status"] = "akshare_live" if any(i.get("price",0)>0 for i in items) else "static"
data["updatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
OUT.parent.mkdir(parents=True, exist_ok=True)
open(OUT, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
print(f"Saved ({len(items)} items)")