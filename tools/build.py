#!/usr/bin/env python3
"""Build the installable web app into dist/ from src/slate.html (the same page published as the Claude artifact)."""
import re, shutil, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, PUBLIC, DIST = ROOT / "src" / "slate.html", ROOT / "public", ROOT / "dist"

page = SRC.read_text()
title = re.search(r"<title>.*?</title>", page, re.S).group(0)
style = re.search(r"<style>.*?</style>", page, re.S).group(0)
body = page.replace(title, "", 1).replace(style, "", 1).strip()

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
{title}
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Slate">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#f2f2f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#111111" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<!-- The page points these at the icon chosen in Settings (Blue, White or Black); these are the defaults. -->
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="favicon.png">
<script>
  window.SLATE_BUILD = "__BUILD__";
  // placement set in Settings > Adjust dock and loading screen, applied before the loading screen draws
  try {{ var tn = JSON.parse(localStorage.getItem("slate.tune") || "{{}}"); [["dockY","--dock-y"],["dockPad","--dock-pad"],["ldExt","--ld-ext"]].forEach(function (p) {{ if (isFinite(tn[p[0]])) document.documentElement.style.setProperty(p[1], tn[p[0]] + "px"); }}); }} catch (e) {{}}
  // iOS 26 home-screen apps: size the page to the whole screen before anything draws (see html.fullh in the styles).
  (function () {{ try {{
    var sa = navigator.standalone === true || (window.matchMedia && matchMedia("(display-mode: standalone)").matches);
    var gap = sa ? Math.round(Math.max(screen.height, window.outerHeight || 0) - window.innerHeight) : 0;
    if (gap > 0 && gap < 120) {{ document.documentElement.classList.add("fullh"); document.documentElement.style.setProperty("--full-h", (window.innerHeight + gap) + "px"); }}
  }} catch (e) {{}} }})();
</script>
<style>body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
{style}
</head>
<body>
"""
sw_register = """<script>
if ("serviceWorker" in navigator) {
  // Pick up new versions without reinstalling: check for an update on open and whenever the app comes back, and reload once when a new version takes over.
  const hadController = !!navigator.serviceWorker.controller; let reloaded = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || reloaded) return; reloaded = true;
    const go = () => { const busy = document.querySelector(".sheet-wrap.open, .ideas-page.open, .side-panel.open") || (document.activeElement && /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)); if (busy) return setTimeout(go, 4000); location.reload(); };
    go();
  });
  addEventListener("load", () => navigator.serviceWorker.register("sw.js").then(reg => {
    const check = () => reg.update().catch(() => {});
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") check(); });
    setInterval(check, 5 * 60 * 1000);
  }).catch(() => {}));
}
</script>"""

if DIST.exists():
    shutil.rmtree(DIST)
shutil.copytree(PUBLIC, DIST)
version = time.strftime("%Y%m%d%H%M%S", time.gmtime())
(DIST / "index.html").write_text((head + body + "\n" + sw_register + "\n</body>\n</html>\n").replace("__BUILD__", version[:4] + "-" + version[4:6] + "-" + version[6:8] + " " + version[8:10] + ":" + version[10:12] + " UTC"))
(DIST / "sw.js").write_text((ROOT / "tools" / "sw.template.js").read_text().replace("__VERSION__", version))
(DIST / ".nojekyll").write_text("")
print(f"Built dist/ (version {version})")
