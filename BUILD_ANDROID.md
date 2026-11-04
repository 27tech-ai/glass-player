# Building the Android (TV) app

The web app is the app: Capacitor wraps it, and the **GlassVlc** plugin adds
the libVLC native engine for everything the web cannot play (RTSP/UDP/AC3/
MPEG-2/MKV…). `capacitor.config.json` is already tuned (appId
`com.lhousin.glassplayer`, cleartext + mixed content allowed for http IPTV
streams, dark launch background).

> Status honesty: the plugin (`android-plugin/GlassVlcPlugin.java`) is an
> integration skeleton implementing the full bridge surface. It has **not**
> been compiled or device-tested from this repo — follow the steps below on a
> machine with the Android SDK, then run the device checklist.

## Prerequisites

- Node.js 18+ and npm
- JDK 17
- Android SDK (command-line tools + platform 34 + build-tools), `ANDROID_HOME` set
- A TV box / emulator for testing (API 24+ recommended)

## Steps

```bash
# 1. Capacitor scaffolding (once)
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap add android

# 2. libVLC dependency — in android/app/build.gradle:
#    implementation 'org.videolan.android:libvlc-all:3.6.0'  (or newer 3.x)

# 3. Install the plugin class
mkdir -p android/app/src/main/java/com/lhousin/glassplayer
cp android-plugin/GlassVlcPlugin.java android/app/src/main/java/com/lhousin/glassplayer/

# 4. Register it — in MainActivity.java:
#    import com.lhousin.glassplayer.GlassVlcPlugin;
#    @Override public void onCreate(Bundle s){ registerPlugin(GlassVlcPlugin.class); super.onCreate(s); }

# 5. Android TV (Leanback) — in android/app/src/main/AndroidManifest.xml,
#    on the <application> and main <activity>:
#    android:banner="@drawable/banner"           (320x180 TV banner)
#    <uses-feature android:name="android.software.leanback" android:required="false"/>
#    <uses-feature android:name="android.hardware.touchscreen" android:required="false"/>
#    and add to the launcher intent-filter:
#    <category android:name="android.intent.category.LEANBACK_LAUNCHER"/>

# 6. Build
npx cap sync android
cd android && ./gradlew assembleDebug     # -> app/build/outputs/apk/debug/app-debug.apk
# Release (needs a keystore configured in gradle):
./gradlew assembleRelease                 # -> app/build/outputs/apk/release/
```

## Two native routes — external VLC app vs embedded libVLC

**Route A — external VLC app (simplest, recommended first).** The plugin's
`hasVlc` / `openExternal` methods fire an Android intent at the installed VLC
app (`org.videolan.vlc`); VLC plays the stream full-screen in its own UI, and
Back returns to Glass Player. Needs NO libVLC Gradle dependency — skip step 2
if you only want this route — but it DOES need package visibility declared in
`AndroidManifest.xml` (Android 11+):

```xml
<queries><package android:name="org.videolan.vlc"/></queries>
```

Trade-offs: playback leaves the Glass Player UI (no merge mode, no built-in
recovery/diagnostics on that route), and VLC must be installed — if it isn't,
the intent rejects and the player automatically falls back to the web chain.

**Route B — embedded libVLC (full control).** Steps 2–4 below. Playback
stays inside the app's own UI; tracks/speed/fit/recovery all remain ours.
Heavier APK, more moving parts.

Routing order in `app.js` is: embedded libVLC → external VLC app → web
chain → honest protocol error. On the web both native routes are absent and
nothing changes.

## How playback routes

`vlc-bridge.js` (already loaded by index.html) is inert on the web. In the
app, `GPNative.available()` is true, so `app.js` hands every channel to
libVLC and the web engines never run. Speed/fit settings route to the plugin
too; quality/audio/subtitle selects remain web-engine controls — wire them to
`GPNative.selectAudio/selectSubtitle` when productizing track menus for the
native path.

## Device test checklist (do not skip)

- [ ] HLS + MP4 + raw TS channels play full-screen, D-pad only
- [ ] An RTSP and a UDP channel play (the whole point of the native engine)
- [ ] An AC3-audio channel has sound
- [ ] Back button: drawer → settings → fullscreen → Home, in that order
- [ ] Home stops the stream (no background audio/data)
- [ ] Kill + relaunch: last playlist auto-restores, nothing autoplays
- [ ] 2-hour live session on the weakest target box: no crash, memory stable
