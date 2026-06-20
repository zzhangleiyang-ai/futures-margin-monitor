import json, os, sys
from tqsdk import TqApi, TqAuth

user = os.environ.get("TQ_USER", "")
passwd = os.environ.get("TQ_PASS", "")
print("User: " + user[:2] + "*** Connected: starting...")

varieties = {
    "SHFE": ["RB","HC","CU","AL","ZN","PB","NI","SN","AU","AG","BU","RU","SP","SS","BR"],
    "DCE": ["I","J","JM","M","Y","A","B","P","C","CS","L","PP","V","EG","EB","JD","LH","PG"],
    "CZCE": ["SR","CF","OI","RM","MA","TA","FG","SA","UR","AP","CJ","SF","SM","PF","PK"],
    "CFFEX": ["IF","IC","IH","IM"],
    "INE": ["SC","NR","LU","BC"],
    "GFEX": ["SI","LC"]
}

results = []
try:
    auth = TqAuth(user, passwd)
    api = TqApi(auth=auth)
    from datetime import datetime
    now = datetime.now(); m = now.month; y = now.year % 100
    
    for ex, codes in varieties.items():
        for vid in codes:
            for j in range(4):
                nxt = m + 1 + j; yr = y
                if nxt > 12: nxt -= 12; yr += 1
                code = vid + str(yr) + str(nxt).zfill(2)
                try:
                    q = api.get_quote(ex + "." + code)
                    if q and q.last_price:
                        results.append({"c": code, "p": float(q.last_price), "o": int(q.open_interest or 0), "r": 0.07})
                except: pass
            found = [r for r in results if r["c"].startswith(vid)]
            if found: print("OK: " + vid + "=" + str(found[0]["p"]))
    api.close()
except Exception as e:
    print("ERR: " + str(e)[:300])

print("Total: " + str(len(results)))
with open("data.json", "w") as f: json.dump(results, f)