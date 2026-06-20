# -*- coding: utf-8 -*-
import json, os, re, sys, subprocess
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(__file__))

from tqsdk import TqApi, TqAuth

PHONE = "zlymds"
PWD = "ZLY123456789"

TQC = {"RB":["SHFE","rb"],"HC":["SHFE","hc"],"CU":["SHFE","cu"],"AL":["SHFE","al"],"ZN":["SHFE","zn"],"PB":["SHFE","pb"],"NI":["SHFE","ni"],"SN":["SHFE","sn"],"AU":["SHFE","au"],"AG":["SHFE","ag"],"BU":["SHFE","bu"],"RU":["SHFE","ru"],"SP":["SHFE","sp"],"SS":["SHFE","ss"],"BR":["SHFE","br"],"I":["DCE","i"],"J":["DCE","j"],"JM":["DCE","jm"],"M":["DCE","m"],"Y":["DCE","y"],"A":["DCE","a"],"B":["DCE","b"],"P":["DCE","p"],"C":["DCE","c"],"CS":["DCE","cs"],"L":["DCE","l"],"PP":["DCE","pp"],"V":["DCE","v"],"EG":["DCE","eg"],"EB":["DCE","eb"],"JD":["DCE","jd"],"LH":["DCE","lh"],"PG":["DCE","pg"],"SR":["CZCE","SR"],"CF":["CZCE","CF"],"OI":["CZCE","OI"],"RM":["CZCE","RM"],"MA":["CZCE","MA"],"TA":["CZCE","TA"],"FG":["CZCE","FG"],"SA":["CZCE","SA"],"UR":["CZCE","UR"],"AP":["CZCE","AP"],"CJ":["CZCE","CJ"],"SF":["CZCE","SF"],"SM":["CZCE","SM"],"PF":["CZCE","PF"],"PK":["CZCE","PK"],"IF":["CFFEX","IF"],"IC":["CFFEX","IC"],"IH":["CFFEX","IH"],"IM":["CFFEX","IM"],"SC":["INE","sc"],"NR":["INE","nr"],"LU":["INE","lu"],"BC":["INE","bc"],"SI":["GFEX","si"],"LC":["GFEX","lc"]}
INFO = {"RB":["SHFE","螺纹钢",10,0.07],"HC":["SHFE","热卷",10,0.07],"CU":["SHFE","沪铜",5,0.08],"AL":["SHFE","沪铝",5,0.08],"ZN":["SHFE","沪锌",5,0.08],"PB":["SHFE","沪铅",5,0.08],"NI":["SHFE","沪镍",1,0.10],"SN":["SHFE","沪锡",1,0.10],"AU":["SHFE","沪金",1000,0.08],"AG":["SHFE","沪银",15,0.09],"BU":["SHFE","沥青",10,0.10],"RU":["SHFE","橡胶",10,0.08],"SP":["SHFE","纸浆",10,0.08],"SS":["SHFE","不锈钢",5,0.10],"BR":["SHFE","合成橡胶",5,0.08],"I":["DCE","铁矿石",100,0.11],"J":["DCE","焦炭",100,0.11],"JM":["DCE","焦煤",60,0.11],"M":["DCE","豆粕",10,0.07],"Y":["DCE","豆油",10,0.07],"A":["DCE","豆一",10,0.08],"B":["DCE","豆二",10,0.08],"P":["DCE","棕榈油",10,0.08],"C":["DCE","玉米",10,0.07],"CS":["DCE","淀粉",10,0.07],"L":["DCE","聚乙烯",5,0.07],"PP":["DCE","聚丙烯",5,0.07],"V":["DCE","聚氯乙烯",5,0.07],"EG":["DCE","乙二醇",10,0.08],"EB":["DCE","苯乙烯",5,0.08],"JD":["DCE","鸡蛋",5,0.08],"LH":["DCE","生猪",16,0.08],"PG":["DCE","液化气",20,0.08],"SR":["CZCE","白糖",10,0.07],"CF":["CZCE","棉花",5,0.07],"OI":["CZCE","菜油",10,0.08],"RM":["CZCE","菜粕",10,0.07],"MA":["CZCE","甲醇",10,0.08],"TA":["CZCE","PTA",5,0.07],"FG":["CZCE","玻璃",20,0.08],"SA":["CZCE","纯碱",20,0.08],"UR":["CZCE","尿素",20,0.08],"AP":["CZCE","苹果",10,0.08],"CJ":["CZCE","红枣",5,0.08],"SF":["CZCE","硅铁",5,0.10],"SM":["CZCE","锰硅",5,0.10],"PF":["CZCE","短纤",5,0.08],"PK":["CZCE","花生",5,0.08],"IF":["CFFEX","沪深300",300,0.12],"IC":["CFFEX","中证500",200,0.12],"IH":["CFFEX","上证50",300,0.12],"IM":["CFFEX","中证1000",200,0.12],"SC":["INE","原油",1000,0.10],"NR":["INE","20号胶",10,0.08],"LU":["INE","低硫燃油",10,0.10],"BC":["INE","国际铜",5,0.08],"SI":["GFEX","工业硅",5,0.09],"LC":["GFEX","碳酸锂",1,0.09]}


def fetch(api):
    results = []
    for vid, (ex, tq) in TQC.items():
        try:
            q = api.get_quote("KQ.m@" + ex + "." + tq)
            if q and q.last_price and q.last_price > 0:
                _, _, _, mr = INFO[vid]
                results.append({"c": vid, "p": round(float(q.last_price), 2), "o": int(q.open_interest or 0), "r": mr})
        except:
            pass
    return results


def update_data_json(data):
    os.makedirs("data", exist_ok=True)
    with open("data/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"已更新 data/data.json ({len(data)} 条)")


def update_index_html(data):
    path = "index.html"
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    ed_str = json.dumps(data, ensure_ascii=False)
    new_html = re.sub(r"var ED=\[.*?\];", "var ED=" + ed_str + ";", html, flags=re.DOTALL)
    if "var ED=[" not in new_html:
        print("错误: 无法替换ED数组")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"已更新 index.html ({len(data)} 条)")


def push():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        r = subprocess.run(["git", "commit", "-m", "Update " + now], capture_output=True, text=True)
        out = (r.stdout or r.stderr or "").strip()[:120]
        print("提交:", out)
        pr = subprocess.run(["git", "push"], capture_output=True, text=True)
        if pr.returncode == 0:
            print("推送成功!")
        else:
            err = (pr.stderr or "").strip()[:200]
            if "up-to-date" in err or "nothing" in err:
                print("数据无变化, 跳过")
            else:
                print("推送失败:", err)
    except Exception as e:
        print("Git错误:", str(e)[:200])


def main():
    print("连接天勤量化...")
    api = TqApi(auth=TqAuth(PHONE, PWD))
    data = fetch(api)
    api.close()
    print(f"获取到 {len(data)} 个品种")
    if not data:
        return
    update_data_json(data)
    update_index_html(data)
    push()


if __name__ == "__main__":
    main()
