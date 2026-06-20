// Auto-refresh futures quotes from Sina Finance every 10 seconds
(function() {
  // Contract list parsed from page
  function getContracts() {
    var cards = document.querySelectorAll('[data-code]');
    var list = [];
    cards.forEach(function(c) { list.push(c.dataset.code); });
    return list;
  }

  function fmtPrice(v) {
    if (v >= 100000) return Math.round(v/10000) + "万";
    if (v >= 1000) return Math.round(v).toLocaleString();
    return v.toFixed(2);
  }
  function fmtOi(v) {
    return v >= 10000 ? (v/10000).toFixed(1) + "万" : String(v);
  }
  function fmtMargin(v) {
    return v >= 10000 ? (v/10000).toFixed(1) + "万元" : Math.round(v).toLocaleString() + "元";
  }

  var loadingEl = null;
  var statusEl = null;
  var contracts = [];
  var intervalId = null;

  function fetchQuotes() {
    if (contracts.length === 0) contracts = getContracts();
    if (contracts.length === 0) return;
    if (!loadingEl) loadingEl = document.getElementById("loadingIndicator");
    if (loadingEl) loadingEl.textContent = "更新中...";

    // Use script tag to bypass CORS
    var s = document.createElement("script");
    var symbols = contracts.join(",");
    symbols = symbols.toUpperCase();
    s.src = "http://hq.sinajs.cn/list=" + symbols + "&_t=" + Date.now();
    document.body.appendChild(s);

    // Parse response after a short delay
    setTimeout(parseData, 600);
  }

  function parseData() {
    try {
      for (var i = 0; i < contracts.length; i++) {
        var sym = contracts[i];
        var varName = "hq_str_" + sym.toUpperCase();
        var raw = window[varName];
        if (!raw) continue;
        var fields = raw.split(",");
        if (fields.length < 10) continue;
        var price = parseFloat(fields[3]);
        var oi = parseFloat(fields[7]);
        if (price <= 0) continue;

        var card = document.querySelector('[data-code="' + sym + '"]');
        if (!card) continue;
        var mult = parseFloat(card.dataset.mult);
        var rate = parseFloat(card.dataset.rate);
        var pEl = document.getElementById("p_" + sym);
        var oiEl = document.getElementById("oi_" + sym);
        var mgEl = document.getElementById("mg_" + sym);
        var mlEl = document.getElementById("ml_" + sym);
        if (pEl) pEl.textContent = fmtPrice(price);
        if (oiEl) oiEl.textContent = fmtOi(oi);
        var margin = price * mult * rate;
        if (mlEl) mlEl.textContent = fmtMargin(margin);
      }
    } catch (e) { console.log(e); }

    if (loadingEl) loadingEl.textContent = "";
    if (!statusEl) statusEl = document.getElementById("updateStatus");
    if (statusEl) statusEl.textContent = new Date().toLocaleTimeString() + " 实时行情";
  }

  // Start
  fetchQuotes();
  intervalId = setInterval(fetchQuotes, 10000);
})();