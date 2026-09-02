/* Service worker — comptage hors-ligne (F3).
 *
 * Deux stratégies seulement, choisies pour un usage en réserve ou en chambre
 * froide où le réseau tombe sans prévenir :
 *  - coquille (CSS/JS/icônes) : cache d'abord, c'est figé entre deux déploiements ;
 *  - pages de comptage : réseau d'abord avec repli sur le cache, pour ne jamais
 *    afficher une liste périmée quand le réseau est là, ni un écran blanc quand
 *    il ne l'est pas.
 * Le reste du site n'est pas mis en cache : hors-ligne, seul le comptage est
 * promis, et mieux vaut une erreur franche qu'un écart calculé sur des
 * chiffres périmés.
 */
// Injecté par la route /sw.js à partir du contenu réel de la coquille et du
// gabarit de comptage (app/main.py, _sw_build_version) : change tout seul
// dès qu'un de ces fichiers change, sans dépendre qu'on y pense au déploiement.
const VERSION = "__BUILD_VERSION__";
const SHELL_CACHE = `shell-${VERSION}`;
const PAGES_CACHE = `pages-${VERSION}`;

const SHELL = [
  "/static/tailwind.css",
  "/static/app.css",
  "/static/app.js",
  // Sans ce script, une page de comptage servie par le cache n'a plus de file
  // hors-ligne : il est pré-chargé, pas seulement mis en cache au passage.
  "/static/offline-count.js",
  "/static/icon-192.png",
  "/static/manifest.webmanifest",
  // Les chiffres du comptage sont le contenu de l'écran : sans ces coupes,
  // une session hors-ligne retomberait sur la police système et les colonnes
  // de nombres cesseraient de s'aligner.
  "/static/fonts/ibm-plex-sans-latin-400-normal.woff2",
  "/static/fonts/ibm-plex-sans-latin-600-normal.woff2",
  "/static/fonts/ibm-plex-mono-latin-400-normal.woff2",
  "/static/fonts/ibm-plex-mono-latin-600-normal.woff2",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => !key.endsWith(VERSION)).map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

const isCountingPage = (url) =>
  url.origin === self.location.origin && /^\/counting(\/\d+)?$/.test(url.pathname);

const isShellAsset = (url) =>
  url.origin === self.location.origin && url.pathname.startsWith("/static/");

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return; // les envois passent par la file locale

  const url = new URL(request.url);

  if (isShellAsset(url)) {
    event.respondWith(
      caches.match(request).then((hit) => hit || fetch(request).then((response) => {
        const copy = response.clone();
        caches.open(SHELL_CACHE).then((cache) => cache.put(request, copy));
        return response;
      }))
    );
    return;
  }

  if (isCountingPage(url)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(PAGES_CACHE).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request).then((hit) => hit || caches.match("/counting")))
    );
  }
});
