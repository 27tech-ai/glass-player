# Playback engines

Glass Player has two engine layers. The **web layer** is what GitHub Pages
serves and needs nothing native. The **Android layer** (libVLC) takes over
wholesale inside the APK, where the web's hard limits disappear.

## Web layer (active everywhere)

Engines, all bundled locally and loaded **lazily** (only when a channel needs
them): native `<video>`, **hls.js** (HLS), **mpegts.js** (raw TS/FLV).
Startup weight stays ~46 KB; engines cost 0 until used.

One click runs a time-boxed (12 s/attempt), sequence-guarded fallback chain —
an error is shown only after *every* attempt fails:

- **File** (mp4/webm/…): native.
- **HLS** (.m3u8): native (if supported) → hls.js direct → hls.js via own
  proxy with IP-alias → hls.js via each proxy → native.
- **TS / no extension**: mpegts.js → hls.js on the Xtream `.m3u8` twin →
  mpegts via own proxy + alias → twin via own proxy + alias → mpegts via
  proxies → twin via proxies → hls.js → native.

Key mechanisms (see `glass-player-src/app.js` outside the minified build):

- **Proxies**: order = your own proxy (`gp-proxy`, set via the `#proxy=`
  setup link) → public proxies (corsproxy.io, allorigins) *if enabled in
  Settings*. LAN addresses are never proxied. Proxied hls.js uses a custom
  loader that rewrites playlist segment URIs against the original URL —
  otherwise segments nest proxies and all fail.
- **IP alias**: Cloudflare Workers refuse raw-IP URLs (`error code: 1003`).
  Via your own proxy, IP hosts are first tried as `<ip>.nip.io`.
- **Xtream twin**: panels that disable `.ts` output often serve the same
  path as `.m3u8`; the twin is attempted early, direct and proxied.
- **Playlist/EPG fetch** (`fetchTextVia`): direct → own proxy + alias →
  proxies. CORS on the playlist itself is routed around the same way.
- **Auto-recovery**: stall watchdog 10 s → hls.js soft recovery → full
  replay, exponential backoff 1.5 s/4 s/9 s, max 3, reset on `playing`.
- **Diagnostics**: the Settings stream-info line records which engine and
  route won (never URLs/credentials).
- **Merge mode**: an external audio URL plays on a hidden `<audio>` element
  (same chain), video muted, 1 s sync loop (hard seek > 2.5 s drift, rate
  nudge 0.94/1.06 between 0.3–2.5 s).
- **Protocols** RTSP/RTMP/UDP/MMS fail fast with an honest explanation.

### Why no Shaka Player

Shaka adds ~600 KB+ (this project's #1 rule is lightness; total startup is
~46 KB) and its unique value is MPEG-DASH — rare in IPTV playlists, and
handled by libVLC in the Android layer. If a real DASH use case appears, the
correct place for it is the native engine, not the web bundle.

### Hard limits of ANY web player (not bugs)

UDP/RTMP/MMS, AC3/E-AC3 audio, MPEG-2/HEVC video on most browsers, DRM,
providers that whitelist another origin or block datacenter IPs. The chain
detects what it can and reports honestly; the fix is the native engine.

## Android layer (libVLC) — status: scaffold

- `vlc-bridge.js` exposes `window.GPNative` (open/play/pause/stop/seek/
  volume/mute/rate/fit/hw-decoding/track selection). On the web
  `available()` is false and the file is inert.
- `app.js`: if `GPNative.available()`, `play()` hands the channel to libVLC
  and the web chain never runs; `destroyEngines()` also stops native.
- `android-plugin/GlassVlcPlugin.java`: Capacitor plugin implementing the
  full method surface on libVLC, with a SurfaceView under the WebView and
  `playing`/`error`/`buffering` events bridged back to the page.
- **Not verified on a device from this repo alone** — build and test steps
  live in BUILD_ANDROID.md. libVLC is what makes RTSP/UDP/AC3/MPEG-2/MKV/AVI
  and DASH play on Android TV boxes.

## Format reality check

A container extension never guarantees the codec inside plays. Web: MP4/WebM
with H.264/VP9/AV1 + AAC/Opus is the safe zone; MKV/AVI containers are not
web-playable regardless of extension tricks. Native (libVLC): plays
essentially all of the above plus TS/M2TS/MPEG/FLV/OGV containers, RTSP/RTMP/
UDP protocols, and AC3/DTS/MPEG-2/HEVC codecs.
