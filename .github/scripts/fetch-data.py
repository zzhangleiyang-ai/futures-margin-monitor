import json, requests
from datetime import datetime
now = datetime.now(); m = now.month; y = now.year % 100
code = "RB" + str(y) + str(m+1).zfill(2)
print("Testing contract:", code)

results = []
ua = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}

# Try East Money with various formats
formats = ["1." + code, "128." + code, "0." + code, code, "hf_" + code]
for secid in formats:
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f5,f8,f12,f14&secids=" + secid
        r = requests.get(url, headers=ua, timeout=5).json()
        rc = r.get("rc", -1)
        if rc == 0 and r.get("data"):
            data = r["data"]
            price = data.get("f2")
            oi = data.get("f8")
            name = data.get("f14")
            print("OK: format=" + secid + " name=" + str(name) + " price=" + str(price) + " oi=" + str(oi))
            if price:
                results.append({"c": code, "p": price, "o": oi or 0, "r": 0.07})
                break
        else:
            print("FAIL: format=" + secid + " rc=" + str(rc))
    except Exception as e:
        print("ERR: format=" + secid + " " + str(e)[:50])

# Try Sina as fallback
if not results:
    ua2 = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"}
    try:
        r = requests.get("https://hq.sinajs.cn/list=hf_" + code, headers=ua2, timeout=5)
        r.encoding = "gbk"
        if '"' in r.text:
            parts = r.text.split('"')
            if len(parts) > 1:
                vals = parts[1].split(",")
                if len(vals) > 10 and vals[3]:
                    price = float(vals[3])
                    oi = int(vals[9]) if vals[9] else 0
                    print("OK: sina price=" + str(price) + " oi=" + str(oi))
                    results.append({"c": code, "p": price, "o": oi, "r": 0.07})
    except Exception as e:
        print("SINA ERR: " + str(e)[:50])

print("Results:", len(results))
with open("data.json", "w") as f:
    json.dump(results, f)