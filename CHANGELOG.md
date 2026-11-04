# Changelog

## v7.5 — 2026-11-04 (external VLC hand-off)

- Android routing is now: **embedded libVLC → external VLC app → web chain**.
  `vlc-bridge.js` gains `hasExternalVlc()` / `openExternal(url)`; the plugin
  gains `hasVlc` (PackageManager) and `openExternal` (VIEW intent targeted at
  `org.videolan.vlc`). If VLC is absent or refuses, playback falls back to
  the web chain automatically. Requires the `<queries>` manifest entry
  documented in BUILD_ANDROID.md (Android 11+ package visibility).
- Web behavior unchanged (both native routes absent); SW cache v15.

## v7.4 — 2026-11-04 (engineering upgrade)

**Added**
- M3U parser hardening: quoted attributes containing commas/spaces, channel
  name taken after the first comma *outside* quotes, `#EXTGRP`, BOM + CRLF
  handling, `tvg-name` fallback, relative URL resolution against the playlist
  URL, bare-URL entries named from their path, duplicate removal.
- Playback diagnostics: Settings shows the winning engine/route/resolution/
  codec for the current channel (e.g. `hls.js · own proxy · IP alias ·
  1920×1080 · avc1+mp4a`). No URLs or credentials are ever shown or logged.
- Settings: playback **speed** select (0.5×–2×) and video **fit** select
  (contain / cover / fill), both persisted and applied to the active engine.
- Settings: **public-proxy toggle** — public CORS proxies are now an optional
  last resort (default on); your own proxy is always first and unaffected.
- Protocol fast-fail: RTSP/RTMP/UDP/MMS links get an immediate, honest
  explanation instead of burning the whole fallback chain.
- Android native engine bridge: `vlc-bridge.js` (inert on the web) +
  `android-plugin/GlassVlcPlugin.java` (libVLC) + `BUILD_ANDROID.md`.
  Status: scaffold, NOT TESTABLE without an Android SDK/device.
- Repo test suite: `tests/run_tests.py` + `tests/RESULTS.md`
  (13 PASS · 0 FAIL · 1 NOT TESTABLE on 2026-11-04).
- Docs: `PLAYBACK_ENGINES.md`, `TROUBLESHOOTING.md`, `BUILD_ANDROID.md`.

**Fixed / improved**
- Auto-recovery now uses exponential backoff (1.5s → 4s → 9s) with a
  readyState guard, still capped at 3 attempts — no retry storms.
- Playlist/EPG fetches already fell back through proxies; parser fixes make
  more real-world playlists load correctly (Xtream exports with commas in
  group names were previously mis-split).

**Removed**
- Nothing. No feature was removed; public proxies were demoted to an
  optional, user-controlled last resort rather than deleted.

**Deliberately NOT added**
- Shaka Player: ~600 KB+ for DASH, which is rare in IPTV playlists and
  contradicts this project's lightness rule. DASH is a native-engine job
  (libVLC plays it on Android). See PLAYBACK_ENGINES.md.

## v7.3 — 2026-11-03
Raw-IP alias fix: Cloudflare Workers refuse IP-literal URLs (error 1003), so
through the user's own proxy the player first tries the `<ip>.nip.io` alias
(HLS/TS/Xtream-twin/merge-audio), and playlist/EPG fetches fall back through
proxies (`fetchTextVia`). One-link proxy setup (`#proxy=`). Personal
Cloudflare Worker support.

## v7.2 — 2026-11-03
Persistence hardened: `gp-last-url` + URL playlists mirrored in localStorage
(survive TV-browser IndexedDB wipes), silent auto-restore without autoplay.

## v7.1 — 2026-11-03
Xtream twin: `.ts` channels also tried as `.m3u8` (panels that disable TS
output), direct and via proxies.

## v7 — 2026-11-02 (FINAL polish)
Auto-recovery (soft hls.js recovery → full replay, max 3), full teardown on
Home, merge-mode crash fix, settings overflow fix, focus/star fixes, complete
fallback chain (native → hls.js → proxies → mpegts.js), merge mode (v6),
bundled engines, ultra-minimal Liquid Glass UI, TV remote navigation, PWA.
