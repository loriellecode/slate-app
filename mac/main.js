// Slate for Mac: a window around the Slate web app (https://loriellecode.github.io/slate-app/).
// The app itself updates whenever the site does, and Slate's own offline cache keeps it working without internet after the first open.
const { app, BrowserWindow, Menu, shell, nativeTheme } = require("electron");
const path = require("path");

const SITE = "https://loriellecode.github.io/slate-app/";
const HOST = new URL(SITE).host;
let win = null;

const offlinePage = `data:text/html;charset=utf-8,${encodeURIComponent(`<!doctype html><meta charset="utf-8"><title>Slate</title>
<style>html,body{height:100%;margin:0;background:#fff;color:#0a0a0a;font:16px -apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif}
body{display:grid;place-items:center;text-align:center}p{color:#8a8a8a;margin:8px 0 22px}
button{font:inherit;border:0;border-radius:999px;padding:12px 26px;background:#0a0a0a;color:#fff;cursor:pointer}</style>
<div><h2 style="font-weight:400;margin:0">Slate can't reach the internet</h2><p>The first time you open Slate it needs a connection. After that it works offline.</p>
<button onclick="location.href='${SITE}'">Try again</button></div>`)}`;

function createWindow() {
  win = new BrowserWindow({
    width: 1180, height: 820, minWidth: 420, minHeight: 600,
    title: "Slate", backgroundColor: "#ffffff", show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: true }
  });
  win.once("ready-to-show", () => win.show());
  win.loadURL(SITE);
  win.webContents.on("did-fail-load", (_e, code, _d, url, isMain) => {
    if (isMain && code !== -3 && url.startsWith(SITE)) win.loadURL(offlinePage);
  });
  // Links to other sites open in the normal browser; Slate stays Slate
  const external = url => { try { if (new URL(url).host !== HOST) { shell.openExternal(url); return true; } } catch (e) {} return false; };
  win.webContents.setWindowOpenHandler(({ url }) => { if (!external(url)) win.loadURL(url); return { action: "deny" }; });
  win.webContents.on("will-navigate", (e, url) => { if (url.startsWith("data:")) return; if (external(url)) e.preventDefault(); });
  win.on("closed", () => { win = null; });
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
else {
  app.on("second-instance", () => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } });
  app.setName("Slate");
  app.whenReady().then(() => {
    nativeTheme.themeSource = "system";
    Menu.setApplicationMenu(Menu.buildFromTemplate([
      { label: "Slate", submenu: [{ role: "about" }, { type: "separator" }, { role: "hide" }, { role: "hideOthers" }, { role: "unhide" }, { type: "separator" }, { role: "quit" }] },
      { label: "Edit", submenu: [{ role: "undo" }, { role: "redo" }, { type: "separator" }, { role: "cut" }, { role: "copy" }, { role: "paste" }, { role: "selectAll" }] },
      { label: "View", submenu: [{ role: "reload" }, { role: "forceReload" }, { type: "separator" }, { role: "resetZoom" }, { role: "zoomIn" }, { role: "zoomOut" }, { type: "separator" }, { role: "togglefullscreen" }] },
      { label: "Window", submenu: [{ role: "minimize" }, { role: "zoom" }, { type: "separator" }, { role: "front" }] }
    ]));
    createWindow();
    app.on("activate", () => { if (!win) createWindow(); else win.show(); });
  });
  app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
}
