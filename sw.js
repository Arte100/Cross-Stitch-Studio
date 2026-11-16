/* The cross stitch tool moved to /stitch/. This retires the offline helper it used at the site root. */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => { e.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter(k => k.startsWith("cross-stitch-studio-")).map(k => caches.delete(k)));
  await self.registration.unregister();
  const pages = await self.clients.matchAll({ type: "window" });
  pages.forEach(p => p.navigate(p.url));
})()); });
