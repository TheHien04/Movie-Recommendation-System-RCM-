const CACHE = 'cinemate-v1'
const ASSETS = ['/', '/index.html']

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)))
})

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET' || e.request.url.includes('/api')) return
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request)),
  )
})
