# GlassVlc plugin

`GlassVlcPlugin.java` — Capacitor plugin bridging the web layer
(`../vlc-bridge.js`, `window.GPNative`) to libVLC on Android.

Implements: open / play / pause / stop / seek / setVolume / mute / setRate /
setFit / setHwDecoding / selectAudio / selectSubtitle, and emits
`playing` / `error` / `buffering` events.

Build + registration + Leanback manifest steps: see `../BUILD_ANDROID.md`.
Status: integration skeleton — not compiled or device-tested from this repo.
