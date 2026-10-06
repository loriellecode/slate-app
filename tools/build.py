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
<link rel="apple-touch-icon" id="touchIcon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" href="favicon-light.png" media="(prefers-color-scheme: light)">
<link rel="icon" type="image/png" href="favicon-dark.png" media="(prefers-color-scheme: dark)">
<script>
  // Home-screen icon: black tile in light mode, white tile in dark mode. iPadOS saves whichever is set when Slate is added.
  (function () {{
    var mq = window.matchMedia && matchMedia("(prefers-color-scheme: dark)");
    function pick() {{ var l = document.getElementById("touchIcon"); if (l) l.href = mq && mq.matches ? "apple-touch-icon-dark.png" : "apple-touch-icon.png"; }}
    pick(); if (mq && mq.addEventListener) mq.addEventListener("change", pick);
  }})();
</script>
<style>body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
{style}
</head>
<body>
"""
sw_register = '<script>if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));</script>'

if DIST.exists():
    shutil.rmtree(DIST)
shutil.copytree(PUBLIC, DIST)
(DIST / "index.html").write_text(head + body + "\n" + sw_register + "\n</body>\n</html>\n")

version = time.strftime("%Y%m%d%H%M%S")
(DIST / "sw.js").write_text((ROOT / "tools" / "sw.template.js").read_text().replace("__VERSION__", version))
(DIST / ".nojekyll").write_text("")
print(f"Built dist/ (version {version})")
