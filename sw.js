// 루멘 카운터 웹(GitHub Pages) 서비스 워커: 홈 화면에 설치(PWA)한 뒤 인터넷 없이도 열리게 함.
// - 화면(HTML)은 인터넷이 되면 늘 새로 받음(업데이트가 바로 반영) → 안 되면 저장해 둔 것으로 엶.
// - 나머지(아이콘·글꼴 등)는 저장해 둔 것을 먼저 쓰고, 없으면 받아서 저장.
// 등록은 lumencalc.html 맨 아래에서 (APK·아티팩트에서는 등록하지 않음).
const CACHE = 'lumencalc-v1';
const PRECACHE = ['./', 'index.html', 'lumencalc.html', 'manifest.webmanifest', 'pwa/icon-192.png', 'pwa/icon-512.png', 'pwa/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const keep = (req, res) => {
  if (res && res.ok) {
    const copy = res.clone(); // 페이지가 본문을 읽기 전에 복사
    caches.open(CACHE).then((c) => c.put(req, copy));
  }
  return res;
};

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 같은 사이트 파일과 숫자 글꼴(Google Fonts)만 다룸
  if (url.origin !== location.origin && url.hostname !== 'fonts.gstatic.com') return;
  if (req.mode === 'navigate' || url.pathname.endsWith('.html')) {
    e.respondWith(fetch(req).then((res) => keep(req, res))
      .catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match('lumencalc.html'))));
    return;
  }
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => keep(req, res))));
});
