# Troubleshooting

First step for any dead channel: open **Settings** after trying it — the
stream-info line tells you which engine/route the player ended on, and the
error toast tells you the failure class. Then find your case below.

| Symptom | Likely cause | What to do |
|---|---|---|
| "Could not play in any mode" on many channels from one provider | Provider blocks browsers (CORS) and/or serves raw-IP links | Set up your own proxy (deploy/DEPLOY.md), open the `#proxy=` setup link once per device. This fixes CORS + mixed content + raw-IP (via the built-in nip.io alias) in one move |
| Channel plays in VLC/TiviMate but never in the browser | Codec (AC3, MPEG-2, HEVC) or protocol (UDP/RTMP) the web cannot decode | Nothing to fix on the web — use the Android app (libVLC engine) for that provider |
| Channel is `rtsp://`, `udp://`, `rtmp://` | Protocol unsupported by all browsers | The player says so immediately. Native app only |
| One channel dead, neighbours fine | Dead/expired token, geo-block, or the channel is simply offline | Check the same link in another player on the same network; if it fails everywhere it's the provider |
| Playlist link "could not load" | Playlist host blocks CORS, or the link is raw-IP | Same own-proxy setup as above — playlist fetching also falls back through your proxy (alias first for IPs) |
| Playlist loads but groups/names look wrong | Non-standard M3U export | v7.4 parser handles quoted commas, EXTGRP, BOM/CRLF, relative URLs. If it still looks wrong, open an issue with a redacted sample |
| Saved playlist disappeared (TV browser) | TV WebViews wipe IndexedDB | Already mitigated: URL playlists + last link are mirrored in localStorage and auto-restore. File playlists are IndexedDB-only (too big for localStorage) — prefer URL playlists on TV |
| Stream plays, then dies and won't recover | Provider drops long connections / token expiry | Built-in recovery retries 3× with backoff, then reports honestly. Re-click the channel for a fresh chain (new token fetch) |
| Video fine, no sound | AC3/DTS audio (web can't decode) or a split audio/video HLS | If the provider offers a separate audio link, paste it in Settings → audio link (merge mode syncs it). Otherwise native app |
| Picture cropped/stretched after changing Fit | Fit = Cover crops, Fill stretches by design | Settings → Fit → Contain restores the full picture |
| Everything slow with a huge playlist | 10k+ channels on a weak box | Search/group filters are instant; rows render lazily (200/page). Prefer trimmed playlists on low-end boxes |
| Public proxies stopped helping | Providers ban public-proxy IPs; corsproxy.io also blocks raw IPs (403) | That's expected — use your own Worker proxy; or turn public proxies OFF in Settings and rely on direct + your proxy |

**Privacy note:** diagnostics and this player never log stream URLs,
usernames, passwords or tokens. Xtream credentials inside a playlist URL
stay in your browser's local storage only.
