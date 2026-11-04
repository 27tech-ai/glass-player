# Test results

Suite: `tests/run_tests.py` — the shipped player in headless Chromium, local
fixture servers (app + ffmpeg-generated HLS/MP4), no internet involved.

## Run — 2026-11-04 (v7.4)

| Check | Result |
|---|---|
| parser: quoted attrs + commas in name/group | PASS |
| parser: BOM + CRLF + #EXTGRP | PASS |
| parser: relative URL resolution | PASS |
| parser: bare URL naming | PASS |
| parser: duplicates removed | PASS |
| proxies: public toggle off/on | PASS |
| proxies: LAN never proxied | PASS |
| ip alias: raw IP → nip.io | PASS |
| xtream twin: .ts → .m3u8 | PASS |
| playback: HLS fixture | PASS |
| playback: MP4 fixture | PASS |
| protocol: RTSP honest fast error | PASS |
| page errors during suite | PASS (0) |
| android: libVLC bridge lifecycle | NOT TESTABLE (needs Android SDK + device) |

**13 PASS · 0 FAIL · 1 NOT TESTABLE**

## Run — 2026-11-04 (v7.5, external VLC hand-off)

Same suite plus: `bridge: no external VLC on web (falls through)` — PASS.
Android intent hand-off itself: NOT TESTABLE (needs a device with VLC).

**14 PASS · 0 FAIL · 2 NOT TESTABLE**

Extended local suites (same day, project test bench): fallback chain incl.
CORS-blocked-via-proxy and dead-channel reporting (5/5 PASS), Cloudflare-1003
simulation with IP playlist + IP channel via nip.io alias (PASS), settings
panel overflow/speed/fit/stream-info checks (PASS). Earlier live verification
against the owner's real Cloudflare Worker + a real public playlist: IP
channel flowed end-to-end through the Worker via the alias (20 requests,
playback clock advanced ~40s).
