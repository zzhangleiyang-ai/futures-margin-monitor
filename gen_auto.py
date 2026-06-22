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
html = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>期货保证金监控</title><style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#0f172a;color:#e2e8f0;margin:0}.hd{background:#1e293b;padding:20px 24px;border-bottom:1px solid #334155}.hi{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:12px}.ht{font-size:20px;font-weight:700;color:#f1f5f9}.hs{font-size:13px;color:#64748b;margin-left:8px}.w{max-width:1400px;margin:0 auto;padding:0 24px}.st{font-size:13px;color:#64748b;margin:16px 0 20px 24px}.se{margin-bottom:20px}.eh{display:flex;align-items:center;padding:12px 16px;border-left:4px solid;background:#1e293b;border-radius:10px 10px 0 0;margin-bottom:2px}.en{font-size:15px;font-weight:600}.ec{font-size:12px;color:#64748b;margin-left:10px}.cg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}.cd{background:#1e293b;border-radius:0 0 10px 10px;padding:14px 16px;border-top:2px solid;border-color:inherit}.ct{display:flex;align-items:baseline;gap:8px;margin-bottom:10px}.cn{font-size:15px;font-weight:600;color:#f1f5f9}.ck{font-size:12px;color:#64748b}.cb{display:flex;justify-content:space-between;align-items:flex-start}.cp{font-size:22px;font-weight:700;color:#facc15}.cr{text-align:right;min-width:120px}.ci{font-size:12px;color:#94a3b8;margin-bottom:4px;display:flex;justify-content:space-between;gap:6px}.ib{color:#e2e8f0;font-weight:600}.im{font-size:14px;font-weight:600;color:#facc15}.tl{display:flex;gap:10px;padding:12px 0;flex-wrap:wrap;align-items:center}.tl input,.tl select,.tl button{height:36px;box-sizing:border-box;border-radius:6px;font-size:13px}.tl input{flex:1;min-width:160px;background:#1e293b;border:1px solid #334155;padding:0 12px;color:#e2e8f0;outline:none}.tl input:focus{border-color:#2563eb}.tl input::placeholder{color:#475569}.tl select{background:#1e293b;border:1px solid #334155;padding:0 10px;color:#e2e8f0;cursor:pointer;min-width:120px}.tl select:focus{border-color:#2563eb}.tl button{background:#2563eb;border:none;padding:0 20px;color:white;cursor:pointer;font-weight:600}.tl button:hover{background:#1d4ed8}.tl button:active{background:#1e40af}.tc{font-size:12px;color:#475569;padding:4px 0 12px}.tc span{color:#e2e8f0;font-weight:600}.rb{background:#2563eb;border:none;border-radius:6px;padding:7px 16px;color:white;font-size:13px;cursor:pointer;font-weight:600}.rb:hover{background:#1d4ed8}.rb:active{background:#1e40af}.ft{max-width:1400px;margin:0 auto;padding:16px 24px 32px;text-align:center;font-size:12px;color:#475569;border-top:1px solid #1e293b}</style></head><body>'
html += '<div class="hd"><div class="hi"><span class="ht">期货保证金监控</span><span class="hs" id="updateStatus">' + d.get('updatedAt','')[:10] + ' 实时行情每10秒更新</span><button class="rb" onclick="fq()">刷新</button></div></div>'
html += '<div class="w tl"><input id="query" type="search" placeholder="搜索品种名称、代码..." autocomplete="off"><select id="exchange"><option value="">全部交易所</option><option value="SHFE">上期所</option><option value="DCE">大商所</option><option value="CZCE">郑商所</option><option value="CFFEX">中金所</option><option value="INE">能源中心</option><option value="GFEX">广期所</option></select><button id="refresh" type="button">刷新</button></div>'

html += '<div class="w tc">共 <span id="totalCount">'+str(len(items))+'</span> 个合约，显示 <span id="visibleCount">'+str(len(items))+'</span> 个</div>'

html += '<div class="w st">' + str(len(items)) + ' 个主力合约(持仓量>3万手) <span id="loadingIndicator" style="color:#facc15;font-size:12px"></span> <span id="selfCheckStatus" style="color:#22c55e;font-size:11px">\u7b49\u5f85\u68c0\u67e5...</span></div><div class="w">'
for ex in ex_order:
    ex_items = [x for x in items if x['exchange']==ex]
    if not ex_items: continue
    html += '<div class="se" data-exchange="'+ex+'"><div class="eh" style="border-color:'+ex_colors[ex]+'"><span class="en" style="color:'+ex_colors[ex]+'">'+ex_names[ex]+'</span><span class="ec">'+str(len(ex_items))+'个品种</span></div><div class="cg">'
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
html += 'var _psnap={};function deepCheck(){var n=document.getElementById("selfCheckStatus");var e=0,s=0,k=0;for(var i=0;i<SC.length;i++){var sm=SC[i];var p=document.getElementById("p_"+sm);if(!p)continue;var v=parseFloat(p.textContent.replace(/[^0-9.\-]/g,""));if(isNaN(v)||v<=0)e++;else{k++;if(_psnap[sm]!==undefined&&_psnap[sm]===v)s++}_psnap[sm]=v}var m="";if(e)m+=e+"异常 ";if(s)m+=s+"未更新 ";if(!m)m="正常";m+=" | "+k+"/"+SC.length;if(n){n.textContent=m;n.style.color=e>0?"#ef4444":s>0?"#eab308":"#22c55e"}if(e||s)console.warn("自检:"+e+"异常",s+"未更新")}function selfCheck(){var e=[],k=0;var n=document.getElementById("selfCheckStatus");for(var i=0;i<SC.length;i++){var sm=SC[i];var pe=document.getElementById("p_"+sm);if(pe){var v=parseFloat(pe.textContent.replace(/[^0-9.\-]/g,""));if(isNaN(v)||v<=0)e.push(sm);else k++}}var msg=k+"/"+SC.length+" \u6b63\u5e38";if(e.length)msg+="; "+e.length+" \u5f02\u5e38";if(n)n.textContent=msg;if(e.length)console.warn("\u81ea\u68c0: "+e.length+" \u4e2a\u5408\u7ea6\u5f02\u5e38: "+e.join(","));return{ok:k,err:e.length}}function fq(){SI.textContent="更新中...";'
html += 'var s=document.createElement("script");'
html += 's.src="https://hq.sinajs.cn/list='+sina_list+'&_t="+Date.now();'
html += 'document.body.appendChild(s);'
html += 'setTimeout(function(){try{for(var i=0;i<SC.length;i++){var sm=SC[i];var v=window["hq_str_"+sm];if(v){var fd=v.split(",");if(fd.length>10){var pr=parseFloat(fd[3]);var o=parseFloat(fd[7]);if(pr>0){var ca=document.querySelector("[data-code=\'"+sm+"\']");if(ca){var mu=parseFloat(ca.dataset.mult);var ra=parseFloat(ca.dataset.rate);var pe=document.getElementById("p_"+sm);var oe=document.getElementById("oi_"+sm);var me=document.getElementById("mg_"+sm);var le=document.getElementById("ml_"+sm);if(pe)pe.textContent=fp(pr);if(oe)oe.textContent=fo(o);var ma=pr*mu*ra;if(le)le.textContent=fm(ma);}}}}}}catch(e){console.log(e)}'
html += 'SI.textContent="";'
html += 'var _ck=selfCheck();SU.textContent=new Date().toLocaleTimeString()+" \u5b9e\u65f6 ("+_ck.ok+"/"+SC.length+")";'
html += '},500);'
html += 's.onerror=function(){SI.textContent="获取失败,10秒后重试";};'
<<<<<<< Updated upstream
html += 'setTimeout(function(){var _h=window["hq_str_"+SC[0].toUpperCase()];if(!_h||_h.length<5){var x=new XMLHttpRequest();x.open("GET","data.json?_t="+Date.now());x.onload=function(){try{var d=JSON.parse(x.responseText);for(var i=0;i<d.items.length;i++){var it=d.items[i];var sy=it.contract;if(!sy)continue;var ca=document.querySelector("[data-code="+sy+"]");if(!ca)continue;var mu=parseFloat(ca.dataset.mult);var ra=parseFloat(ca.dataset.rate);var pe=document.getElementById("p_"+sy);var oe=document.getElementById("oi_"+sy);var le=document.getElementById("ml_"+sy);if(pe)pe.textContent=fp(it.price);if(oe)oe.textContent=fo(it.openInterest);var ma=it.price*mu*ra;if(le)le.textContent=fm(ma);}}catch(e){console.log(e)}SI.textContent="";var _ck=selfCheck();SU.textContent=new Date().toLocaleTimeString()+" 缓存数据("+_ck.ok+"/"+SC.length+")";};x.send()}},800);'
=======
html += 'setTimeout(function(){var _h=window["hq_str_"+SC[0]];if(!_h||_h.length<5){var x=new XMLHttpRequest();x.open("GET","data.json?_t="+Date.now());x.onload=function(){try{var d=JSON.parse(x.responseText);for(var i=0;i<d.items.length;i++){var it=d.items[i];var sy=it.contract;if(!sy)continue;var ca=document.querySelector("[data-code="+sy+"]");if(!ca)continue;var mu=parseFloat(ca.dataset.mult);var ra=parseFloat(ca.dataset.rate);var pe=document.getElementById("p_"+sy);var oe=document.getElementById("oi_"+sy);var le=document.getElementById("ml_"+sy);if(pe)pe.textContent=fp(it.price);if(oe)oe.textContent=fo(it.openInterest);var ma=it.price*mu*ra;if(le)le.textContent=fm(ma);}}catch(e){console.log(e)}SI.textContent="";var _ck=selfCheck();SU.textContent=new Date().toLocaleTimeString()+" 缓存数据("+_ck.ok+"/"+SC.length+")";};x.send()}},800);'
>>>>>>> Stashed changes
html += '}'
html += 'function filterCards(){var q=document.getElementById("query").value.trim().toLowerCase();var e=document.getElementById("exchange").value;var cards=document.querySelectorAll(".cd");var show=0;var secs=document.querySelectorAll(".se");for(var i=0;i<cards.length;i++){var c=cards[i];var t=c.textContent.toLowerCase();var ex=c.closest(".se");var exCode=ex?ex.dataset.exchange||"":"";var ok=(!q||t.indexOf(q)>-1)&&(!e||exCode===e);c.style.display=ok?"":"none";if(ok)show++}for(var j=0;j<secs.length;j++){var s=secs[j];var a=s.querySelectorAll(".cd");var h=true;for(var k=0;k<a.length;k++){if(a[k].style.display!=="none"){h=false;break}}s.style.display=h?"none":""}document.getElementById("visibleCount").textContent=show}'

html += 'document.getElementById("query").addEventListener("input",filterCards);'

html += 'document.getElementById("exchange").addEventListener("change",filterCards);'

html += 'document.getElementById("refresh").addEventListener("click",function(){location.reload()});'

html += 'fq();'

html += 'setInterval(fq,10000);setTimeout(deepCheck,3000);setInterval(deepCheck,300000);'
html += '</script></body></html>'
for fn in ['index.html','docs/index.html']:
    with open(os.path.join(base,fn),'w',encoding='utf-8') as f:
        f.write(html)
print('OK',len(html),'bytes')



