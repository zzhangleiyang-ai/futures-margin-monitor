import json, requests, sys
from datetime import datetime

now = datetime.now(); m = now.month; yr = now.year % 100

# All varieties
varieties = ['RB','HC','CU','AL','ZN','PB','NI','SN','AU','AG','BU','RU','SP','SS','BR','I','J','JM','M','Y','A','B','P','C','CS','L','PP','V','EG','EB','JD','LH','PG','SR','CF','OI','RM','MA','TA','FG','SA','UR','AP','CJ','SF','SM','PF','PK','IF','IC','IH','IM','SC','NR','LU','BC','SI','LC']

all_codes = []
for v in varieties:
    for j in range(4):
        nxt = m + 1 + j; y = yr
        if nxt > 12: nxt -= 12; y += 1
        all_codes.append(v + str(y) + str(nxt).zfill(2))

results = []
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Referer':'https://quote.eastmoney.com/'}

# Try East Money with different market codes
for market in ['1.', '128.', '0.', '100.']:
    if results: break
    batch_size = 100
    for i in range(0, len(all_codes), batch_size):
        batch = all_codes[i:i+batch_size]
        secids = market + (',' + market).join(batch)
        secids = secids.rstrip('.')
        url = 'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f5,f8,f12,f14&secids=' + secids
        try:
            r = requests.get(url, headers=headers, timeout=8).json()
            if r.get('data') and r['data'].get('diff'):
                for item in r['data']['diff']:
                    if item.get('f2') and item.get('f12'):
                        results.append({'c':item['f12'],'p':item['f2'],'o':int(item.get('f8',0)),'r':0.07,'ch':item.get('f3',0)})
        except:
            pass
        if len([x for x in results if x.get('c')]) > 50: break

# Try Sina if no results
if not results:
    h2 = {'User-Agent':'Mozilla/5.0','Referer':'https://finance.sina.com.cn/'}
    batch_size = 50
    for i in range(0, len(all_codes), batch_size):
        batch = all_codes[i:i+batch_size]
        codes = ','.join(['hf_'+c for c in batch])
        try:
            r = requests.get('https://hq.sinajs.cn/list=' + codes, headers=h2, timeout=8)
            r.encoding = 'gbk'
            for line in r.text.split(';'):
                if '=' in line:
                    parts = line.split('=')
                    vn = parts[0].strip()
                    if vn.startswith('var hq_str_hf_'):
                        code = vn.replace('var hq_str_hf_','')
                        vals = parts[1].strip().strip('"').split(',')
                        if len(vals) > 10 and vals[3]:
                            results.append({'c':code,'p':float(vals[3]),'o':int(vals[9]) if vals[9] else 0,'r':0.07,'ch':0})
        except:
            pass
        if results: break

print(json.dumps({'fetched':len(results)}))
with open('data.json','w') as f: json.dump(results, f)
