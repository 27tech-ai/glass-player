# Glass Player — Light M3U / M3U8 Player

The lightest complete web player: **no framework, no build step**, just HTML + CSS + vanilla JS.
Works in any modern browser (Chrome, Safari, Firefox, Edge, Samsung Internet, most TV browsers).

## Run it
- Easiest: open `index.html` in a browser. (Loading a playlist **file** works even from `file://`.)
- Better (enables PWA / service worker): serve the folder, e.g.
  `npx serve .` or `python3 -m http.server` then open the shown URL.
## What it does — ULTRA minimal UI, Ionicons, essential icons only
The screen shows **almost nothing**. Home: the **link input + 2 icons**. Player: the video +
**4 icons**, auto-hidden while playing (any mouse move / touch / remote key brings them back).
All icons are **Ionicons** (https://ionic.io/ionicons), embedded locally as SVG — no emoji,
no icon font, works offline. There are **no empty-state or instructional texts**: if there is
no content (e.g. no EPG guide for a channel), **nothing is shown at all**.

Essential icons kept — everything else was removed:
| Where | Icons |
|---|---|
| Home | Load link (arrow-forward) · Open file (folder-open) |
| Player | Home (home) · Channels (list) · Settings (settings) · Fullscreen (expand) |
| Inside panels only | Close, All/Favorites/Recent, Favorite star, Show more, Delete, Dark/Light |

- Loads `.m3u` / `.m3u8` playlists **from a URL or from a file** (drag & drop works too), parses
  `#EXTINF` names, `tvg-id`, `tvg-logo` and `group-title`.
- Search + group filter, chunked rendering (200 at a time) so huge playlists stay fast & light.
- **Playback engine with auto-fallback** — one click tries every way a browser can play
  the stream, and only errors after all of them fail:
  mp4/webm → native · `.m3u8` → native (Safari/TV) → bundled **hls.js** → hls.js via a
  **CORS proxy** (fixes CORS-blocked providers and http-streams on https pages) → native ·
  `.ts` / extension-less Xtream-style streams → bundled **mpegts.js** → hls.js → native.
  Every attempt is time-boxed (12s), so a dead channel reports in seconds, never minutes.
  Both engines are bundled (`hls.min.js`, `mpegts.min.js`) — no CDN can be blocked or hang.
- Optional: use your own CORS proxy instead of the public fallbacks —
  in the browser console: `localStorage.setItem('gp-proxy', JSON.stringify('https://your-proxy/?url='))`
- **Favorites** and **Recently watched** (inside the Channels panel), saved on the device.
- **EPG** (XMLTV): paste the EPG link into the **same** home input (or open an XML file) —
  the app detects it automatically. Current + next programme show under the channel name;
  no guide = nothing shown.
- **Saved playlists**: URL and file playlists are saved (IndexedDB) and appear **by themselves**
  under the home input when they exist — no library button.
- **Settings panel**: quality, **audio track**, **subtitles**, and the **Dark/Light** toggle.
- **Resume**: films/VOD resume where you stopped (live streams are never resumed).
- **Apple Liquid Glass design** — one design system only (glass tokens, blur, soft dark palette,
  comfortable for the eyes), Dark mode by default.
- **Tablet / TV:** larger icons and channel panel on tablets; on big TV screens the UI scales
  up automatically (no TV-mode button).
- **TV Box remote:** no mouse needed. D-pad arrows move a big visible focus ring,
  OK/Enter selects/plays, on the player ←/→ seek 10s, ↑/↓ volume,
  Back/Esc closes panels / exits fullscreen / returns home.
  Samsung TV Back (10009) and LG Back (461) key codes are handled.
- **PWA:** installable, offline app shell, ready to wrap as an APK.
- No Chromecast, no Picture-in-Picture — this is a TV player, by design.

## Important limitation (all web players have it)
Some playlist providers block browsers with **CORS**. If a URL fails, the app tells you —
download that playlist and open it **as a file**, which always works.
Also, `http://` streams can be blocked on `https://` pages (mixed content) — serve the app
over `http://` on your local network (e.g. on the TV box itself) if your streams are http-only.

## Convert to APK (pick one)
### A. Capacitor (recommended, real Android app)
```bash
npm init -y
npm i @capacitor/core @capacitor/cli @capacitor/android
npx cap init "Glass Player" com.example.glassplayer --web-dir=.
npx cap add android
npx cap sync
npx cap open android   # then Build > Build APK in Android Studio
```
A ready `capacitor.config.json` is included.
### B. PWA → APK (no code)
Host this folder on https, open it in Chrome Android → “Install app”,
or generate an APK from the PWA with **Bubblewrap** (`npx @bubblewrap/cli init`) or PWABuilder.com.
### C. Simple WebView wrapper
Create an Android Studio “Empty Activity” project, add a WebView, load your hosted URL
(or `file:///android_asset/` with these files copied into `assets/`). Enable JavaScript +
`mediaPlaybackRequiresUserGesture = false`.

## Files
| File | Role |
|---|---|
| `index.html` | App structure |
| `style.css` | Liquid Glass design system (tokens in `:root`) |
| `app.js` | M3U parser, playback (fast-fail timeouts), remote navigation, theme |
| `hls.min.js` | hls.js 1.5.13 (MIT), bundled — HLS playback without any CDN |
| `mpegts.min.js` | mpegts.js 1.7.3 (Apache-2.0), bundled — MPEG-TS / FLV stream playback |
| `manifest.webmanifest` + `sw.js` | PWA / offline shell |
| `sample.m3u` | Public test streams for a 1-click demo |
| `icon.svg`, `icon-192.png`, `icon-512.png` | App icons |

License: free to use and modify.

## Merge mode (separate audio link)
If a channel has picture but its sound lives on a **separate link**: play the channel,
open ⚙ Settings, paste the audio link into **"Audio link…"** and press the 🔗 button.
The player mutes the video, plays the audio on its own engine (HLS / TS / MP3-AAC…) and
keeps the two in sync (drift is corrected every second; pause/seek/volume stay linked).
Press 🔗 again to unmerge. Changing channel unmerges automatically.

## Final polish (v7 — the APK-wrap candidate)
- **Auto-recovery**: if a playing stream drops mid-playback (server hiccup, token refresh),
  the player heals itself — soft hls.js recovery first, then a full channel replay, up to
  3 tries — before it ever shows "Stream lost". Rebuffering shows the spinner only when it lasts.
- Going back Home **stops the stream completely** (no background downloading).
- **5000+ channel playlists** stay smooth: chunked rendering, instant search, and the
  remote's up/down hops row-to-row without scanning the whole list.
- TV detection widened (TV/HbbTV/Fire TV/Bravia/WebOS user agents, pointer-less big screens).
- Settings panel fits its glass exactly; favorite stars render in theme color (gold when on).

## Wrapping the APK (Capacitor — config is ready)
`capacitor.config.json` is already tuned for IPTV on Android TV:
`allowMixedContent: true` + `cleartext: true` (most streams are plain http — without this the
WebView blocks them), dark background `#0b1020` (no white flash at launch), appId
`com.lhousin.glassplayer`. Build:
```
npm init -y && npm i @capacitor/core @capacitor/cli @capacitor/android
npx cap add android && npx cap sync
npx cap open android   # then Build > Build APK in Android Studio
```
For a TV box, also tick "Android TV" / leanback in the manifest if you want it on the TV home row.

## Deploy as a website (GitHub Pages / Cloudflare Pages)
This repo is deploy-ready: a GitHub Actions workflow republishes GitHub Pages on every push,
and a `_headers` file tunes Cloudflare Pages caching/privacy. Step-by-step for both hosts —
plus a free personal CORS-proxy Worker that makes more channels play — is in
[`deploy/DEPLOY.md`](deploy/DEPLOY.md).
