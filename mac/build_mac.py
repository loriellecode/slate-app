#!/usr/bin/env python3
"""Build Slate.app for macOS from Linux: Electron's prebuilt app + main.js, ad-hoc signed with rcodesign, zipped.
Needs (downloaded beforehand): /tmp/el/el-{arm64,x64}.zip (electron-v33.2.1-darwin-*.zip) and rcodesign on PATH or RCODESIGN."""
import os, plistlib, shutil, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
EL = Path(os.environ.get("EL_DIR", "/tmp/el")); OUT = Path(os.environ.get("OUT_DIR", "/tmp/slate-mac-out"))
RC = os.environ.get("RCODESIGN", "rcodesign")
def run(*a, **k): subprocess.run(list(map(str, a)), check=True, **k)
def icns(dst):
    im = Image.open(ROOT / "public" / "icon-512.png").convert("RGB").resize((1024, 1024), Image.LANCZOS)
    im.save(dst, format="ICNS")
for arch in sys.argv[1:] or ["arm64", "x64"]:
    work = OUT / arch; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    run("unzip", "-q", EL / f"el-{arch}.zip", "-d", work)
    app = work / "Slate.app"; (work / "Electron.app").rename(app)
    macos = app / "Contents" / "MacOS"; (macos / "Electron").rename(macos / "Slate")
    res = app / "Contents" / "Resources"
    (res / "default_app.asar").unlink(missing_ok=True); (res / "electron.icns").unlink(missing_ok=True)
    icns(res / "slate.icns")
    (res / "app").mkdir(); shutil.copy(HERE / "main.js", res / "app" / "main.js"); shutil.copy(HERE / "package.json", res / "app" / "package.json")
    pl = app / "Contents" / "Info.plist"; d = plistlib.loads(pl.read_bytes())
    d.update({"CFBundleName": "Slate", "CFBundleDisplayName": "Slate", "CFBundleExecutable": "Slate", "CFBundleIdentifier": "com.slate.planner",
              "CFBundleIconFile": "slate.icns", "CFBundleShortVersionString": "1.0.0", "CFBundleVersion": "1.0.0", "NSHumanReadableCopyright": "Slate"})
    for k in ("ElectronAsarIntegrity", "NSAppleEventsUsageDescription"): d.pop(k, None)
    pl.write_bytes(plistlib.dumps(d))
    run(RC, "sign", app)   # ad-hoc signature: Apple Silicon refuses to start unsigned code
    zp = OUT / f"Slate-mac-{'apple-silicon' if arch == 'arm64' else 'intel'}.zip"; zp.unlink(missing_ok=True)
    run("zip", "-qry", "-X", zp, "Slate.app", cwd=work)
    print("built", zp, round(zp.stat().st_size / 1e6), "MB")
