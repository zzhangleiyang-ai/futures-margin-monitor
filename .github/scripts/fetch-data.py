import json, os, base64, urllib.request
from tqsdk import TqApi, TqAuth

INFO={"RB":["SHFE","螺纹钢",10,0.07],"HC":["SHFE","热卷",10,0.07],"CU":["SHFE","沪铜",5,0.08],"AL":["SHFE","沪铝",5,0.08],"ZN":["SHFE","沪锌",5,0.08],"PB":["SHFE","沪铅",5,0.08],"NI":["SHFE","沪镍",1,0.10],"SN":["SHFE","沪锡",1,0.10],"AU":["SHFE","沪金",1000,0.08],"AG":["SHFE","沪银",15,0.09],"BU":["SHFE","沥青",10,0.10],"RU":["SHFE","橡胶",10,0.08],"SP":["SHFE","纸浆",10,0.08],"SS":["SHFE","不锈钢",5,0.10],"BR":["SHFE","合成橡胶",5,0.08],"I":["DCE","铁矿石",100,0.11],"J":["DCE","焦炭",100,0.11],"JM":["DCE","焦煤",60,0.11],"M":["DCE","豆粕",10,0.07],"Y":["DCE","豆油",10,0.07],"A":["DCE","豆一",10,0.08],"B":["DCE","豆二",10,0.08],"P":["DCE","棕榈油",10,0.08],"C":["DCE","玉米",10,0.07],"CS":["DCE","淀粉",10,0.07],"L":["DCE","聚乙烯",5,0.07],"PP":["DCE","聚丙烯",5,0.07],"V":["DCE","聚氯乙烯",5,0.07],"EG":["DCE","乙二醇",10,0.08],"EB":["DCE","苯乙烯",5,0.08],"JD":["DCE","鸡蛋",5,0.08],"LH":["DCE","生猪",16,0.08],"PG":["DCE","液化气",20,0.08],"SR":["CZCE","白糖",10,0.07],"CF":["CZCE","棉花",5,0.07],"OI":["CZCE","菜油",10,0.08],"RM":["CZCE","菜粕",10,0.07],"MA":["CZCE","甲醇",10,0.08],"TA":["CZCE","PTA",5,0.07],"FG":["CZCE","玻璃",20,0.08],"SA":["CZCE","纯碱",20,0.08],"UR":["CZCE","尿素",20,0.08],"AP":["CZCE","苹果",10,0.08],"CJ":["CZCE","红枣",5,0.08],"SF":["CZCE","硅铁",5,0.10],"SM":["CZCE","锰硅",5,0.10],"PF":["CZCE","短纤",5,0.08],"PK":["CZCE","花生",5,0.08],"IF":["CFFEX","沪深300",300,0.12],"IC":["CFFEX","中证500",200,0.12],"IH":["CFFEX","上证50",300,0.12],"IM":["CFFEX","中证1000",200,0.12],"SC":["INE","原油",1000,0.10],"NR":["INE","20号胶",10,0.08],"LU":["INE","低硫燃油",10,0.10],"BC":["INE","国际铜",5,0.08],"SI":["GFEX","工业硅",5,0.09],"LC":["GFEX","碳酸锂",1,0.09]}
TQC={"RB":["SHFE","rb"],"HC":["SHFE","hc"],"CU":["SHFE","cu"],"AL":["SHFE","al"],"ZN":["SHFE","zn"],"PB":["SHFE","pb"],"NI":["SHFE","ni"],"SN":["SHFE","sn"],"AU":["SHFE","au"],"AG":["SHFE","ag"],"BU":["SHFE","bu"],"RU":["SHFE","ru"],"SP":["SHFE","sp"],"SS":["SHFE","ss"],"BR":["SHFE","br"],"I":["DCE","i"],"J":["DCE","j"],"JM":["DCE","jm"],"M":["DCE","m"],"Y":["DCE","y"],"A":["DCE","a"],"B":["DCE","b"],"P":["DCE","p"],"C":["DCE","c"],"CS":["DCE","cs"],"L":["DCE","l"],"PP":["DCE","pp"],"V":["DCE","v"],"EG":["DCE","eg"],"EB":["DCE","eb"],"JD":["DCE","jd"],"LH":["DCE","lh"],"PG":["DCE","pg"],"SR":["CZCE","SR"],"CF":["CZCE","CF"],"OI":["CZCE","OI"],"RM":["CZCE","RM"],"MA":["CZCE","MA"],"TA":["CZCE","TA"],"FG":["CZCE","FG"],"SA":["CZCE","SA"],"UR":["CZCE","UR"],"AP":["CZCE","AP"],"CJ":["CZCE","CJ"],"SF":["CZCE","SF"],"SM":["CZCE","SM"],"PF":["CZCE","PF"],"PK":["CZCE","PK"],"IF":["CFFEX","IF"],"IC":["CFFEX","IC"],"IH":["CFFEX","IH"],"IM":["CFFEX","IM"],"SC":["INE","sc"],"NR":["INE","nr"],"LU":["INE","lu"],"BC":["INE","bc"],"SI":["GFEX","si"],"LC":["GFEX","lc"]}

try:
    api = TqApi(auth=TqAuth(os.environ["TQ_USER"], os.environ["TQ_PASS"]))
    results = []
    for vid,(ex,tq) in TQC.items():
        q = api.get_quote("KQ.m@" + ex + "." + tq)
        if q and q.last_price:
            ex2,n,m,mr = INFO[vid]
            results.append({"c":vid,"p":float(q.last_price),"o":int(q.open_interest or 0),"n":n,"e":ex2,"m":m,"mr":mr})
    api.close()
    print("OK: " + str(len(results)))
    dj = json.dumps(results, ensure_ascii=False)
    with open("data.json","w",encoding="utf-8") as f: f.write(dj)
    # Try API upload
    token = os.environ.get("GITHUB_TOKEN","")
    if token:
        url = "https://api.github.com/repos/zzhangleiyang-ai/futures-margin-monitor/contents/data/data.json"
        req = urllib.request.Request(url)
        req.add_header("Authorization","Bearer "+token)
        sha = json.loads(urllib.request.urlopen(req).read())["sha"]
        pl = json.dumps({"message":"Update","content":base64.b64encode(dj.encode()).decode(),"sha":sha,"branch":"main"}).encode()
        r2 = urllib.request.Request(url,data=pl,method="PUT")
        r2.add_header("Authorization","Bearer "+token)
        r2.add_header("Content-Type","application/json")
        urllib.request.urlopen(r2)
        print("Uploaded via API")
except Exception as e:
    print("ERR: " + str(e)[:300])

with open("data.json","w") as f: json.dump(results, f)
