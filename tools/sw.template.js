// Network first, so every new version shows up on the next open; the cache only covers offline use.
// It never touches localStorage, where Slate keeps your data.
const CACHE = "slate-__VERSION__";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "favicon.png"];

// The app icon is a date tile, so icon files are drawn here with today's date (works offline). If drawing isn't possible the plain files are used.
const ICON_SIZE = { "icon-192.png": 192, "icon-512.png": 512, "apple-touch-icon.png": 180 };
const EN = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const FONT = '-apple-system, "SF Pro Display", system-ui, "Helvetica Neue", Helvetica, Arial, sans-serif';
async function dateTile(size) {
  const d = new Date(), c = new OffscreenCanvas(size, size), x = c.getContext("2d");
  x.fillStyle = "#fff"; x.fillRect(0, 0, size, size); // square and opaque: iOS rounds it and paints clear pixels black
  x.fillStyle = "#007AFF"; x.textAlign = "center"; x.textBaseline = "alphabetic";
  const fit = (txt, px, wt, maxW, y, ls) => {
    x.font = `${wt} ${px}px ${FONT}`; if ("letterSpacing" in x) x.letterSpacing = (ls || 0) + "px";
    const w = x.measureText(txt).width; if (w > maxW) x.font = `${wt} ${px * maxW / w}px ${FONT}`;
    x.fillText(txt, size / 2, y);
  };
  fit(EN[d.getDay()], size * .165, 600, size * .7, size * .285, size * .012);
  fit(String(d.getDate()), size * .6, 300, size * .74, size * .805, 0);
  return new Response(await c.convertToBlob({ type: "image/png" }), { headers: { "Content-Type": "image/png", "Cache-Control": "no-store" } });
}
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  if (e.request.destination === "video" || e.request.headers.has("range")) return; // let the browser stream video itself
  const file = new URL(e.request.url).pathname.split("/").pop();
  if (ICON_SIZE[file] && typeof OffscreenCanvas !== "undefined") {
    e.respondWith(dateTile(ICON_SIZE[file]).catch(() => fetch(e.request).catch(() => caches.match(e.request))));
    return;
  }
  e.respondWith(
    fetch(e.request, { cache: "no-cache" })
      .then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});
