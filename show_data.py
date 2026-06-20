import json
with open(r'C:\Users\张雷洋\Documents\sxf\_futures-repo\data\data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 品种中文名映射
FC = {"RB":"螺纹钢","HC":"热卷","CU":"沪铜","AL":"沪铝","ZN":"沪锌","PB":"沪铅","NI":"沪镍","SN":"沪锡","AU":"沪金","AG":"沪银","BU":"沥青","RU":"橡胶","SP":"纸浆","SS":"不锈钢","BR":"合成橡胶","I":"铁矿石","J":"焦炭","JM":"焦煤","M":"豆粕","Y":"豆油","A":"豆一","B":"豆二","P":"棕榈油","C":"玉米","CS":"淀粉","L":"聚乙烯","PP":"聚丙烯","V":"聚氯乙烯","EG":"乙二醇","EB":"苯乙烯","JD":"鸡蛋","LH":"生猪","PG":"液化气","SR":"白糖","CF":"棉花","OI":"菜油","RM":"菜粕","MA":"甲醇","TA":"PTA","FG":"玻璃","SA":"纯碱","UR":"尿素","AP":"苹果","CJ":"红枣","SF":"硅铁","SM":"锰硅","PF":"短纤","PK":"花生","IF":"沪深300","IC":"中证500","IH":"上证50","IM":"中证1000","SC":"原油","NR":"20号胶","LU":"低硫燃油","BC":"国际铜","SI":"工业硅","LC":"碳酸锂"}
# 合约乘数
MULT = {"RB":10,"HC":10,"CU":5,"AL":5,"ZN":5,"PB":5,"NI":1,"SN":1,"AU":1000,"AG":15,"BU":10,"RU":10,"SP":10,"SS":5,"BR":5,"I":100,"J":100,"JM":60,"M":10,"Y":10,"A":10,"B":10,"P":10,"C":10,"CS":10,"L":5,"PP":5,"V":5,"EG":10,"EB":5,"JD":5,"LH":16,"PG":20,"SR":10,"CF":5,"OI":10,"RM":10,"MA":10,"TA":5,"FG":20,"SA":20,"UR":20,"AP":10,"CJ":5,"SF":5,"SM":5,"PF":5,"PK":5,"IF":300,"IC":200,"IH":300,"IM":200,"SC":1000,"NR":10,"LU":10,"BC":5,"SI":5,"LC":1}

print(f"共 {len(data)} 个品种")
print()
h = f"{'品种':<6} {'最新价':<10} {'持仓量':<10} {'保证金比例':<6} {'单手保证金':<12} {'总保证金(万)':<10}"
print(h)
print("-" * 60)

# 按总保证金排序
ex_data = sorted(data, key=lambda x: x['o'] * x['p'] * x['r'], reverse=True)

for d in ex_data:
    c = d['c']
    name = FC.get(c, c)
    m = MULT.get(c, 1)
    margin_per = d['p'] * m * d['r']
    total_m = margin_per * d['o'] / 10000
    print(f"{name:<6} {d['p']:<10.2f} {d['o']:<10,} {d['r']*100:<6.1f}% {margin_per:<12,.2f} {total_m:<10,.0f}")
print()
print("JSON原始数据:")
print(json.dumps(data, ensure_ascii=False))
