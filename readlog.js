/* Read-tracking widget for explainer pages.
   Log every time you actually finish reading a paper (separate from rate.js's "was it worth it"
   rating). Saved to localStorage['paperReadLog'][slug] as an array of ISO timestamps — one entry
   per read, so re-reading a paper logs another entry rather than overwriting the last one (shared
   origin, so index.html's Done view and the digest can read it too). Self-contained; guides load
   it with <script src="../readlog.js"></script>, right after rate.js. Theme-aware: mirrors
   whatever the page's own dark-mode toggle set on <html data-theme>. Sits bottom-LEFT so it never
   collides with rate.js's bottom-right pill or the dark-mode toggle's top-right button. */
(function () {
  var slug = (location.pathname.split("/").pop() || "").replace(/\.html$/, "");
  if (!slug) return;
  var KEY = "paperReadLog";
  var LOG = {};
  try { LOG = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
  function save() { localStorage.setItem(KEY, JSON.stringify(LOG)); }
  function entries() { return LOG[slug] || []; }
  function logRead() { LOG[slug] = entries().concat([new Date().toISOString()]); save(); }
  function undoLast() { var e = entries(); if (e.length) { e.pop(); if (e.length) LOG[slug] = e; else delete LOG[slug]; save(); } }
  function dark() { return document.documentElement.getAttribute("data-theme") === "dark"; }
  function fmt(iso) { try { return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }); } catch (e) { return iso; } }
  function relative(iso) {
    var days = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000);
    if (days <= 0) return "today"; if (days === 1) return "yesterday"; if (days < 30) return days + "d ago";
    return fmt(iso);
  }

  var wrap = document.createElement("div");
  wrap.style.cssText = "position:fixed;left:16px;bottom:16px;z-index:99999;font-family:'Mulish',system-ui,sans-serif;display:flex;align-items:center;gap:6px";
  var histOpen = false;

  function render() {
    var d = dark(), e = entries();
    var bg = d ? "#221E17" : "#FFFDF8", border = d ? "#4A4335" : "#D8C8AC", ink = d ? "#ECE4D6" : "#332C24",
      inkSoft = d ? "#B6AB98" : "#6E6456", line = d ? "#38332A" : "#E7DBC6";
    var label = e.length ? "✓ Read " + e.length + "× · " + relative(e[e.length - 1]) : "◻ Mark as read";
    var color = e.length ? "#1f5b51" : ink;
    var pillBg = e.length ? (d ? "#1c332e" : "#DCEFE9") : bg;
    var pillBorder = e.length ? "#2C8C7C" : border;
    var html = '<button id="rl-pill" title="Click to log another read" style="background:' + pillBg + ';border:1.5px solid ' + pillBorder + ';'
      + 'border-radius:999px;padding:9px 14px;box-shadow:0 4px 14px rgba(0,0,0,' + (d ? '.4' : '.16') + ');cursor:pointer;'
      + 'font-weight:800;font-size:.82rem;color:' + color + '">' + label + '</button>';
    if (e.length) {
      html += '<button id="rl-hist" title="Reading history" style="width:30px;height:30px;border-radius:50%;border:1.5px solid ' + border
        + ';background:' + bg + ';color:' + inkSoft + ';cursor:pointer;font-size:.78rem;display:flex;align-items:center;justify-content:center;padding:0">▾</button>';
    }
    if (histOpen && e.length) {
      var rows = e.slice().reverse().map(function (iso, i) {
        return '<div style="display:flex;justify-content:space-between;gap:10px;padding:4px 0;font-size:.78rem;color:' + inkSoft + '">'
          + '<span>' + fmt(iso) + '</span>' + (i === 0 ? '<span data-undo="1" style="cursor:pointer;color:#C0563B">undo</span>' : '') + '</div>';
      }).join('');
      html += '<div id="rl-panel" style="position:absolute;left:0;bottom:44px;background:' + bg + ';border:1.5px solid ' + border
        + ';border-radius:12px;padding:10px 14px;min-width:170px;box-shadow:0 8px 22px rgba(0,0,0,' + (d ? '.5' : '.18') + ')">'
        + '<div style="font-weight:800;font-size:.74rem;color:' + ink + ';margin-bottom:4px">Read ' + e.length + '×</div>' + rows + '</div>';
    }
    wrap.innerHTML = html;
  }
  wrap.addEventListener("click", function (ev) {
    if (ev.target.id === "rl-pill") { logRead(); return render(); }
    if (ev.target.id === "rl-hist") { histOpen = !histOpen; return render(); }
    if (ev.target.getAttribute && ev.target.getAttribute("data-undo")) { undoLast(); histOpen = entries().length > 0 && histOpen; return render(); }
  });
  document.addEventListener("click", function (ev) {
    if (histOpen && !wrap.contains(ev.target)) { histOpen = false; render(); }
  });
  render();
  document.body.appendChild(wrap);
  new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
})();
