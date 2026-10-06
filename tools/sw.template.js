// Network first, so every new version shows up on the next open; the cache only covers offline use.
// It never touches localStorage, where Slate keeps your data.
const CACHE = "slate-__VERSION__";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "apple-touch-icon-dark.png", "favicon-light.png", "favicon-dark.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  if (e.request.destination === "video" || e.request.headers.has("range")) return; // let the browser stream video itself
  e.respondWith(
    fetch(e.request, { cache: "no-cache" })
      .then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});
