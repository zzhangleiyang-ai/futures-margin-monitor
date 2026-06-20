import json, os
from tqsdk import TqApi, TqAuth

PM = {
    "RB":("SHFE","rb"),"HC":("SHFE","hc"),"CU":("SHFE","cu"),"AL":("SHFE","al"),
    "ZN":("SHFE","zn"),"PB":("SHFE","pb"),"NI":("SHFE","ni"),"SN":("SHFE","sn"),
    "AU":("SHFE","au"),"AG":("SHFE","ag"),"BU":("SHFE","bu"),"RU":("SHFE","ru"),
    "SP":("SHFE","sp"),"SS":("SHFE","ss"),"BR":("SHFE","br"),
    "I":("DCE","i"),"J":("DCE","j"),"JM":("DCE","jm"),"M":("DCE","m"),"Y":("DCE","y"),
    "A":("DCE","a"),"B":("DCE","b"),"P":("DCE","p"),"C":("DCE","c"),"CS":("DCE","cs"),
    "L":("DCE","l"),"PP":("DCE","pp"),"V":("DCE","v"),"EG":("DCE","eg"),"EB":("DCE","eb"),
    "JD":("DCE","jd"),"LH":("DCE","lh"),"PG":("DCE","pg"),
    "SR":("CZCE","SR"),"CF":("CZCE","CF"),"OI":("CZCE","OI"),"RM":("CZCE","RM"),
    "MA":("CZCE","MA"),"TA":("CZCE","TA"),"FG":("CZCE","FG"),"SA":("CZCE","SA"),
    "UR":("CZCE","UR"),"AP":("CZCE","AP"),"CJ":("CZCE","CJ"),"SF":("CZCE","SF"),
    "SM":("CZCE","SM"),"PF":("CZCE","PF"),"PK":("CZCE","PK"),
    "IF":("CFFEX","IF"),"IC":("CFFEX","IC"),"IH":("CFFEX","IH"),"IM":("CFFEX","IM"),
    "SC":("INE","sc"),"NR":("INE","nr"),"LU":("INE","lu"),"BC":("INE","bc"),
    "SI":("GFEX","si"),"LC":("GFEX","lc")}
MR = {"RB":0.07,"HC":0.07,"CU":0.08,"AL":0.08,"ZN":0.08,"PB":0.08,"NI":0.12,"SN":0.12,"AU":0.08,"AG":0.09,"BU":0.10,"RU":0.08,"SP":0.08,"SS":0.10,"BR":0.10,"I":0.11,"J":0.20,"JM":0.20,"M":0.07,"Y":0.07,"A":0.07,"B":0.07,"P":0.08,"C":0.06,"CS":0.06,"L":0.08,"PP":0.08,"V":0.08,"EG":0.08,"EB":0.08,"JD":0.08,"LH":0.08,"PG":0.08,"SR":0.07,"CF":0.07,"OI":0.07,"RM":0.07,"MA":0.08,"TA":0.07,"FG":0.09,"SA":0.09,"UR":0.07,"AP":0.08,"CJ":0.10,"SF":0.10,"SM":0.10,"PF":0.07,"PK":0.07,"IF":0.10,"IC":0.12,"IH":0.10,"IM":0.12,"SC":0.10,"NR":0.08,"LU":0.10,"BC":0.08,"SI":0.08,"LC":0.09}

try:
    api = TqApi(auth=TqAuth(os.environ["TQ_USER"], os.environ["TQ_PASS"]))
    results = []
    for vid,(ex,code) in PM.items():
        q = api.get_quote("KQ.m@" + ex + "." + code)
        if q and q.last_price:
            results.append({"c": vid, "p": float(q.last_price), "o": int(q.open_interest or 0), "r": MR.get(vid, 0.07)})
    api.close()
    print("OK: " + str(len(results)) + " varieties")
    with open("data.json", "w") as f: json.dump(results, f)
except Exception as e:
    print("ERR: " + str(e)[:300])
    with open("data.json", "w") as f: json.dump([], f)