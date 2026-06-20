import json, requests, sys
from datetime import datetime
now = datetime.now(); m = now.month; y = now.year % 100
varieties = ['RB','HC','CU','AL','ZN','PB','NI','SN','AU','AG','BU','RU','SP','SS','BR','I','J','JM','M','Y','A','B','P','C','CS','L','PP','V','EG','EB','JD','LH','PG','SR','CF','OI','RM','MA','TA','FG','SA','UR','AP','CJ','SF','SM','PF','PK','IF','IC','IH','IM','SC','NR','LU','BC','SI','LC']
results = []; h = {'User-Agent':'Mozilla/5.0','Referer':'https://quote.eastmoney.com/'}
for vid in varieties:
    found = False
    for j in range(4):
        nxt = m + 1 + j; yr = y
        if nxt > 12: nxt -= 12; yr += 1
        code = vid + str(yr) + str(nxt).zfill(2)
        r = requests.get('https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f5,f8,f12,f14&secids=1.' + code, headers=h, timeout=5).json()
        if r.get('data') and r['data'].get('diff'):
            for item in r['data']['diff']:
                if item.get('f2') and item.get('f12'):
                    try:
                        results.append({'c':item['f12'],'p':float(item['f2']),'o':int(item.get('f8',0)),'ch':float(item.get('f3',0))})
                        found = True
                    except: pass
                break
        if found: break
    if not found:
        # Try Sina as fallback
        h2 = {'User-Agent':'Mozilla/5.0','Referer':'https://finance.sina.com.cn/'}
        for j in range(4):
            nxt = m + 1 + j; yr = y
            if nxt > 12: nxt -= 12; yr += 1
            code = vid + str(yr) + str(nxt).zfill(2)
            try:
                resp = requests.get('https://hq.sinajs.cn/list=hf_' + code, headers=h2, timeout=5)
                resp.encoding = 'gbk'
                if 'hq_str_hf_' in resp.text and '"' in resp.text:
                    parts = resp.text.split('"')[1].split(',')
                    if len(parts) > 10 and parts[3]:
                        results.append({'c':code,'p':float(parts[3]),'o':int(parts[9]) if parts[9] else 0,'ch':0})
                        break
            except: pass
print(json.dumps({'count':len(results),'samples':results[:3]}))