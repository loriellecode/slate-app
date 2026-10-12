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
(DIST / "index.html").write_text(head + body + "\n" + sw_register + "\n</body>\n</html>\n")

version = time.strftime("%Y%m%d%H%M%S")
(DIST / "sw.js").write_text((ROOT / "tools" / "sw.template.js").read_text().replace("__VERSION__", version))
(DIST / ".nojekyll").write_text("")
print(f"Built dist/ (version {version})")
