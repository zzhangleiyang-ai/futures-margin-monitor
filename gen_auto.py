import json, os
base = r'C:\Users\张雷洋\Documents\sxf\futures-margin-monitor'
os.chdir(base)
with open(os.path.join(base,'data.json'),'r',encoding='utf-8') as f:
    d = json.load(f)
items = d['items']
ex_order = ['SHFE','DCE','CZCE','CFFEX','INE','GFEX']
ex_names = {'SHFE':'上期所','DCE':'大商所','CZCE':'郑商所','CFFEX':'中金所','INE':'能源中心','GFEX':'广期所'}
ex_colors = {'SHFE':'#2563eb','DCE':'#059669','CZCE':'#d97706','CFFEX':'#7c3aed','INE':'#0891b2','GFEX':'#db2777'}
sina_list = ','.join([x["contract"] for x in items])
html = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>期货保证金监控</title><style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#0f172a;color:#e2e8f0;margin:0}.hd{background:#1e293b;padding:20px 24px;border-bottom:1px solid #334155}.hi{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:12px}.ht{font-size:20px;font-weight:700;color:#f1f5f9}.hs{font-size:13px;color:#64748b;margin-left:8px}.w{max-width:1400px;margin:0 auto;padding:0 24px}.st{font-size:13px;color:#64748b;margin:16px 0 20px 24px}.se{margin-bottom:20px}.eh{display:flex;align-items:center;padding:12px 16px;border-left:4px solid;background:#1e293b;border-radius:10px 10px 0 0;margin-bottom:2px}.en{font-size:15px;font-weight:600}.ec{font-size:12px;color:#64748b;margin-left:10px}.cg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}.cd{background:#1e293b;border-radius:0 0 10px 10px;padding:14px 16px;border-top:2px solid;border-color:inherit}.ct{display:flex;align-items:baseline;gap:8px;margin-bottom:10px}.cn{font-size:15px;font-weight:600;color:#f1f5f9}.ck{font-size:12px;color:#64748b}.cb{display:flex;justify-content:space-between;align-items:flex-start}.cp{font-size:22px;font-weight:700;color:#facc15}.cr{text-align:right;min-width:120px}.ci{font-size:12px;color:#94a3b8;margin-bottom:4px;display:flex;justify-content:space-between;gap:6px}.ib{color:#e2e8f0;font-weight:600}.im{font-size:14px;font-weight:600;color:#facc15}.ft{max-width:1400px;margin:0 auto;padding:16px 24px 32px;text-align:center;font-size:12px;color:#475569;border-top:1px solid #1e293b}</style></head><body>'
html += '<div class="hd"><div class="hi"><span class="ht">期货保证金监控</span><span class="hs" id="updateStatus">' + d.get('updatedAt','')[:10] + ' 实时行情每10秒更新</span></div></div>'
html += '<div class="w st">' + str(len(items)) + ' 个主力合约(持仓量>3万手) <span id="loadingIndicator" style="color:#facc15;font-size:12px"></span></div><div class="w">'
for ex in ex_order:
    ex_items = [x for x in items if x['exchange']==ex]
    if not ex_items: continue
    html += '<div class="se"><div class="eh" style="border-color:'+ex_colors[ex]+'"><span class="en" style="color:'+ex_colors[ex]+'">'+ex_names[ex]+'</span><span class="ec">'+str(len(ex_items))+'个品种</span></div><div class="cg">'
    for x in ex_items:
        code = x['code']; name = x['name']; p = x['price']; oi = x['openInterest']; m = x['contractMultiplier']
        rate = x['marginRate']; ml = x['marginPerLot']
        if p >= 1000 or p == int(p):
            ps = f'{int(p):,}'
        else:
            ps = f'{p:,.2f}'
        ois = f'{oi/10000:.1f}万' if oi>=10000 else str(oi)
        rp = int(rate*100)
        ms = f'{ml/10000:.1f}万元' if ml>=10000 else f'{ml:.0f}元'
        sym = x["contract"]
        html += '<div class="cd" style="border-color:'+ex_colors[ex]+'" data-code="'+sym+'" data-mult="'+str(m)+'" data-rate="'+str(rate)+'"><div class="ct"><span class="cn">'+name+'</span><span class="ck">'+code+'</span><span class="ck" style="font-size:11px;color:#64748b">['+sym+']</span></div><div class="cb"><div class="cp" id="p_'+sym+'">'+ps+'</div><div class="cr"><div class="ci"><span>持仓</span><strong class="ib" id="oi_'+sym+'">'+ois+'</strong></div><div class="ci"><span>保证金</span><strong class="ib" style="color:'+ex_colors[ex]+'" id="mg_'+sym+'">'+str(rp)+'%</strong></div><div class="ci"><span>每手</span><strong class="im" id="ml_'+sym+'">'+ms+'</strong></div></div></div></div>'
    html += '</div></div>'
html += '</div><div class="ft">实时行情来源:新浪财经 每10秒自动更新 价格自动刷新，保证金率同步计算</div>'
html += '<script>'
html += 'var SC="' + sina_list + '".split(",");'
html += 'var SI=document.getElementById("loadingIndicator");'
html += 'var SU=document.getElementById("updateStatus");'
html += 'function fp(v){if(v>=1000||Number.isInteger(v))return Math.round(v).toLocaleString();return v.toFixed(2);}'
html += 'function fo(v){return v>=10000?(v/10000).toFixed(1)+"万":String(v);}'
html += 'function fm(v){return v>=10000?(v/10000).toFixed(1)+"万元":Math.round(v).toLocaleString()+"元";}'
html += 'function fq(){SI.textContent="更新中...";'
html += 'var s=document.createElement("script");'
html += 's.src="http://hq.sinajs.cn/list='+sina_list+'&_t="+Date.now();'
html += 'document.body.appendChild(s);'
html += 'setTimeout(function(){try{for(var i=0;i<SC.length;i++){var sm=SC[i];var v=window["hq_str_"+sm.toUpperCase()];if(v){var fd=v.split(",");if(fd.length>10){var pr=parseFloat(fd[3]);var o=parseFloat(fd[7]);if(pr>0){var ca=document.querySelector("[data-code=\'"+sm+"\']");if(ca){var mu=parseFloat(ca.dataset.mult);var ra=parseFloat(ca.dataset.rate);var pe=document.getElementById("p_"+sm);var oe=document.getElementById("oi_"+sm);var me=document.getElementById("mg_"+sm);var le=document.getElementById("ml_"+sm);if(pe)pe.textContent=fp(pr);if(oe)oe.textContent=fo(o);var ma=pr*mu*ra;if(le)le.textContent=fm(ma);}}}}}catch(e){console.log(e)}'
html += 'SI.textContent="";'
html += 'SU.textContent=new Date().toLocaleTimeString()+" 实时";'
html += '},500);'
html += 's.onerror=function(){SI.textContent="获取失败,10秒后重试";};'
html += '}'
html += 'fq();'
html += 'setInterval(fq,10000);'
html += '</script></body></html>'
for fn in ['index.html','docs/index.html']:
    with open(os.path.join(base,fn),'w',encoding='utf-8') as f:
        f.write(html)
print('OK',len(html),'bytes')



