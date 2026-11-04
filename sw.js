/* App-shell cache only — streams & playlists are never cached (keeps it light & fresh). */
const C = 'glass-player-v14';
const SHELL = ['./', './index.html', './style.css', './app.js', './vlc-bridge.js', './hls.min.js', './mpegts.min.js', './manifest.webmanifest', './icon.svg', './sample.m3u', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(C).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request)));
});
