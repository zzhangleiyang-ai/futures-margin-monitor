import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data.json"
OUTPUTS = [BASE / "index.html", BASE / "docs" / "index.html"]
EX_ORDER = ["SHFE", "DCE", "CZCE", "CFFEX", "INE", "GFEX"]
EX_NAMES = {
    "SHFE": "上期所",
    "DCE": "大商所",
    "CZCE": "郑商所",
    "CFFEX": "中金所",
    "INE": "能源中心",
    "GFEX": "广期所",
}
EX_COLORS = {
    "SHFE": "#2563eb",
    "DCE": "#059669",
    "CZCE": "#d97706",
    "CFFEX": "#7c3aed",
    "INE": "#0891b2",
    "GFEX": "#db2777",
}


def fmt_price(value):
    if value is None:
        return "--"
    if value >= 1000 or float(value).is_integer():
        return f"{int(round(value)):,}"
    return f"{value:,.2f}"


def fmt_oi(value):
    if value is None:
        return "--"
    return f"{value / 10000:.1f}万" if value >= 10000 else str(int(value))


def fmt_margin(value):
    if value is None:
        return "--"
    return f"{value / 10000:.1f}万元" if value >= 10000 else f"{value:.0f}元"


def build_card(item, exchange):
    color = EX_COLORS[exchange]
    contract = item.get("contract", "")
    rate = item.get("marginRate") or 0
    multiplier = item.get("contractMultiplier") or 0
    return f"""
<div class="cd" style="border-color:{color}" data-code="{contract}" data-mult="{multiplier}" data-rate="{rate}">
  <div class="ct">
    <span class="cn">{item.get("name", "")}</span>
    <span class="ck">{item.get("code", "")}</span>
    <span class="ck" style="font-size:11px;color:#64748b">[{contract}]</span>
  </div>
  <div class="cb">
    <div class="cp" id="p_{contract}">{fmt_price(item.get("price"))}</div>
    <div class="cr">
      <div class="ci"><span>持仓</span><strong class="ib" id="oi_{contract}">{fmt_oi(item.get("openInterest"))}</strong></div>
      <div class="ci"><span>保证金</span><strong class="ib" style="color:{color}" id="mg_{contract}">{int(round(rate * 100))}%</strong></div>
      <div class="ci"><span>每手</span><strong class="im" id="ml_{contract}">{fmt_margin(item.get("marginPerLot"))}</strong></div>
    </div>
  </div>
</div>
""".strip()


def build_html(payload):
    items = payload["items"]
    sections = []
    for exchange in EX_ORDER:
        ex_items = [item for item in items if item.get("exchange") == exchange]
        if not ex_items:
            continue
        cards = "\n".join(build_card(item, exchange) for item in ex_items)
        sections.append(
            f"""
<div class="se" data-exchange="{exchange}">
  <div class="eh" style="border-color:{EX_COLORS[exchange]}">
    <span class="en" style="color:{EX_COLORS[exchange]}">{EX_NAMES[exchange]}</span>
    <span class="ec">{len(ex_items)}个品种</span>
  </div>
  <div class="cg">
    {cards}
  </div>
</div>
""".strip()
        )

    updated_at = str(payload.get("updatedAt", ""))
    last_attempt_at = str(payload.get("lastAttemptAt", ""))
    message = str(payload.get("message", ""))
    display_message = (
        "本次抓取失败，当前显示最近一次有效数据"
        if "using cached data after fetch error" in message
        else (message or "数据同步正常")
    )
    updated_date = updated_at[:10]
    total = len(items)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>期货保证金监控</title>
  <style>
    body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#0f172a;color:#e2e8f0;margin:0}}
    .hd{{background:#1e293b;padding:20px 24px;border-bottom:1px solid #334155}}
    .hi{{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:12px}}
    .ht{{font-size:20px;font-weight:700;color:#f1f5f9}}
    .hs{{font-size:13px;color:#64748b;margin-left:8px}}
    .w{{max-width:1400px;margin:0 auto;padding:0 24px}}
    .st{{font-size:13px;color:#64748b;margin:16px 0 20px 24px}}
    .se{{margin-bottom:20px}}
    .eh{{display:flex;align-items:center;padding:12px 16px;border-left:4px solid;background:#1e293b;border-radius:10px 10px 0 0;margin-bottom:2px}}
    .en{{font-size:15px;font-weight:600}}
    .ec{{font-size:12px;color:#64748b;margin-left:10px}}
    .cg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}}
    .cd{{background:#1e293b;border-radius:0 0 10px 10px;padding:14px 16px;border-top:2px solid;border-color:inherit}}
    .ct{{display:flex;align-items:baseline;gap:8px;margin-bottom:10px}}
    .cn{{font-size:15px;font-weight:600;color:#f1f5f9}}
    .ck{{font-size:12px;color:#64748b}}
    .cb{{display:flex;justify-content:space-between;align-items:flex-start}}
    .cp{{font-size:22px;font-weight:700;color:#facc15}}
    .cr{{text-align:right;min-width:120px}}
    .ci{{font-size:12px;color:#94a3b8;margin-bottom:4px;display:flex;justify-content:space-between;gap:6px}}
    .ib{{color:#e2e8f0;font-weight:600}}
    .im{{font-size:14px;font-weight:600;color:#facc15}}
    .tl{{display:flex;gap:10px;padding:12px 0;flex-wrap:wrap;align-items:center}}
    .tl input,.tl select,.tl button{{height:36px;box-sizing:border-box;border-radius:6px;font-size:13px}}
    .tl input{{flex:1;min-width:160px;background:#1e293b;border:1px solid #334155;padding:0 12px;color:#e2e8f0;outline:none}}
    .tl input:focus,.tl select:focus{{border-color:#2563eb}}
    .tl input::placeholder{{color:#475569}}
    .tl select{{background:#1e293b;border:1px solid #334155;padding:0 10px;color:#e2e8f0;cursor:pointer;min-width:120px}}
    .tl button{{background:#2563eb;border:none;padding:0 20px;color:white;cursor:pointer;font-weight:600}}
    .tl button:hover{{background:#1d4ed8}}
    .tc{{font-size:12px;color:#475569;padding:4px 0 12px}}
    .tc span{{color:#e2e8f0;font-weight:600}}
    .rb{{background:#2563eb;border:none;border-radius:6px;padding:7px 16px;color:white;font-size:13px;cursor:pointer;font-weight:600}}
    .ft{{max-width:1400px;margin:0 auto;padding:16px 24px 32px;text-align:center;font-size:12px;color:#475569;border-top:1px solid #1e293b}}
  </style>
</head>
<body>
  <div class="hd">
    <div class="hi">
      <span class="ht">期货保证金监控</span>
      <span class="hs" id="updateStatus">{updated_date} 每1分钟检查最新数据</span>
      <button class="rb" onclick="refreshData(true)">刷新</button>
    </div>
  </div>
  <div class="w tl">
    <input id="query" type="search" placeholder="搜索品种名称、代码..." autocomplete="off">
    <select id="exchange">
      <option value="">全部交易所</option>
      <option value="SHFE">上期所</option>
      <option value="DCE">大商所</option>
      <option value="CZCE">郑商所</option>
      <option value="CFFEX">中金所</option>
      <option value="INE">能源中心</option>
      <option value="GFEX">广期所</option>
    </select>
    <button id="refresh" type="button">刷新</button>
  </div>
  <div class="w tc">共 <span id="totalCount">{total}</span> 个合约，显示 <span id="visibleCount">{total}</span> 个</div>
  <div class="w st">
    <span>后台数据时间：<strong id="dataUpdatedAt" style="color:#e2e8f0;font-weight:600">{updated_at}</strong></span>
    <span style="margin-left:16px">最近尝试刷新：<strong id="lastAttemptAt" style="color:#94a3b8;font-weight:600">{last_attempt_at}</strong></span>
    <span style="margin-left:16px">页面检查时间：<strong id="pageCheckedAt" style="color:#94a3b8;font-weight:600">--</strong></span>
    <span style="margin-left:16px">更新状态：<strong id="syncStatus" style="font-weight:600;color:#22c55e">正常</strong></span>
    <span id="dataMessage" style="color:#94a3b8;font-size:12px;margin-left:16px">{display_message}</span>
    <span id="loadingIndicator" style="color:#facc15;font-size:12px;margin-left:16px"></span>
  </div>
  <div class="w">
    {"".join(sections)}
  </div>
  <div class="ft">数据源：AKShare，后台自动同步，页面自动检查更新</div>
  <script>
    const loading = document.getElementById("loadingIndicator");
    const updateStatus = document.getElementById("updateStatus");
    const dataUpdatedAtEl = document.getElementById("dataUpdatedAt");
    const lastAttemptAtEl = document.getElementById("lastAttemptAt");
    const pageCheckedAtEl = document.getElementById("pageCheckedAt");
    const syncStatusEl = document.getElementById("syncStatus");
    const dataMessageEl = document.getElementById("dataMessage");
    let lastUpdatedAt = {json.dumps(payload.get("updatedAt", ""))};

    function fmtCheckTime() {{
      return new Date().toLocaleTimeString("zh-CN", {{ hour12: false }});
    }}

    function fmtDataTime(value) {{
      if (!value) return "--";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString("zh-CN", {{ hour12: false }});
    }}

    function fmtMessage(value) {{
      if (!value) return "数据同步正常";
      if (String(value).includes("using cached data after fetch error")) {{
        return "本次抓取失败，当前显示最近一次有效数据";
      }}
      return value;
    }}

    function updateSyncStatus(value, failed) {{
      if (!syncStatusEl) return;
      if (failed) {{
        syncStatusEl.textContent = "检查失败";
        syncStatusEl.style.color = "#ef4444";
        return;
      }}
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {{
        syncStatusEl.textContent = "等待同步";
        syncStatusEl.style.color = "#eab308";
        return;
      }}
      const ageMinutes = (Date.now() - date.getTime()) / 60000;
      if (ageMinutes <= 2) {{
        syncStatusEl.textContent = "正常";
        syncStatusEl.style.color = "#22c55e";
      }} else if (ageMinutes <= 10) {{
        syncStatusEl.textContent = "轻微延迟";
        syncStatusEl.style.color = "#eab308";
      }} else {{
        syncStatusEl.textContent = "延迟较大";
        syncStatusEl.style.color = "#ef4444";
      }}
    }}

    function fmtPrice(value) {{
      if (value == null || Number.isNaN(Number(value))) return "--";
      const num = Number(value);
      if (num >= 1000 || Number.isInteger(num)) return Math.round(num).toLocaleString();
      return num.toFixed(2);
    }}

    function fmtOi(value) {{
      const num = Number(value || 0);
      return num >= 10000 ? (num / 10000).toFixed(1) + "万" : String(Math.round(num));
    }}

    function fmtMargin(value) {{
      const num = Number(value || 0);
      return num >= 10000 ? (num / 10000).toFixed(1) + "万元" : Math.round(num).toLocaleString() + "元";
    }}

    function applyData(payload) {{
      if (!payload || !Array.isArray(payload.items)) return;
      payload.items.forEach((item) => {{
        const code = item.contract;
        if (!code) return;
        const priceEl = document.getElementById("p_" + code);
        const oiEl = document.getElementById("oi_" + code);
        const lotEl = document.getElementById("ml_" + code);
        if (priceEl) priceEl.textContent = fmtPrice(item.price);
        if (oiEl) oiEl.textContent = fmtOi(item.openInterest);
        if (lotEl) lotEl.textContent = fmtMargin(item.marginPerLot);
      }});
      if (payload.updatedAt) {{
        lastUpdatedAt = payload.updatedAt;
        updateStatus.textContent = payload.updatedAt.slice(0, 10) + " 每1分钟自动检查";
        if (dataUpdatedAtEl) dataUpdatedAtEl.textContent = fmtDataTime(payload.updatedAt);
        updateSyncStatus(payload.updatedAt, false);
      }}
      if (lastAttemptAtEl) lastAttemptAtEl.textContent = fmtDataTime(payload.lastAttemptAt);
      if (dataMessageEl) dataMessageEl.textContent = fmtMessage(payload.message);
    }}

    async function refreshData(manual) {{
      if (manual) loading.textContent = "更新中...";
      try {{
        const response = await fetch("data.json?_t=" + Date.now(), {{ cache: "no-store" }});
        const payload = await response.json();
        applyData(payload);
        if (pageCheckedAtEl) pageCheckedAtEl.textContent = fmtCheckTime();
        loading.textContent = "";
      }} catch (error) {{
        if (pageCheckedAtEl) pageCheckedAtEl.textContent = fmtCheckTime();
        loading.textContent = "更新失败";
        updateSyncStatus(lastUpdatedAt, true);
      }}
    }}

    function filterCards() {{
      const query = document.getElementById("query").value.trim().toLowerCase();
      const exchange = document.getElementById("exchange").value;
      const cards = document.querySelectorAll(".cd");
      const sections = document.querySelectorAll(".se");
      let visible = 0;
      cards.forEach((card) => {{
        const text = card.textContent.toLowerCase();
        const ex = card.closest(".se")?.dataset.exchange || "";
        const matched = (!query || text.includes(query)) && (!exchange || ex === exchange);
        card.style.display = matched ? "" : "none";
        if (matched) visible += 1;
      }});
      sections.forEach((section) => {{
        const hasVisible = [...section.querySelectorAll(".cd")].some((card) => card.style.display !== "none");
        section.style.display = hasVisible ? "" : "none";
      }});
      document.getElementById("visibleCount").textContent = visible;
    }}

    document.getElementById("query").addEventListener("input", filterCards);
    document.getElementById("exchange").addEventListener("change", filterCards);
    document.getElementById("refresh").addEventListener("click", () => refreshData(true));

    refreshData(false);
    setInterval(() => refreshData(false), 60000);
  </script>
</body>
</html>
"""


def main():
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    html = build_html(payload)
    for path in OUTPUTS:
        path.write_text(html, encoding="utf-8")
    print(f"OK {len(html)} bytes")


if __name__ == "__main__":
    main()
