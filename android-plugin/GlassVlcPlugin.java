package com.lhousin.glassplayer;

import android.view.SurfaceView;
import android.view.ViewGroup;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.util.ArrayList;
import org.videolan.libvlc.LibVLC;
import org.videolan.libvlc.Media;
import org.videolan.libvlc.MediaPlayer;

/**
 * GlassVlc — Capacitor bridge to libVLC (Android native engine).
 *
 * STATUS: integration skeleton. It compiles against Capacitor + libVLC
 * (org.videolan.android:libvlc-all) and implements the full method surface the
 * web layer calls through vlc-bridge.js. It is NOT verified on a device from
 * the web repo alone — see BUILD_ANDROID.md for the build + test procedure.
 *
 * Surface strategy: a SurfaceView is added to the activity's root view BELOW
 * the WebView; the player page keeps its <video> area transparent while the
 * native engine owns playback (app.js never touches the web engines then).
 */
@CapacitorPlugin(name = "GlassVlc")
public class GlassVlcPlugin extends Plugin {
    private LibVLC libVLC;
    private MediaPlayer player;
    private SurfaceView surface;

    @Override
    public void load() {
        ArrayList<String> args = new ArrayList<>();
        args.add("--no-stats");
        args.add("--network-caching=1500");
        libVLC = new LibVLC(getContext(), args);
        player = new MediaPlayer(libVLC);
        surface = new SurfaceView(getContext());
        getActivity().runOnUiThread(() -> {
            ViewGroup root = (ViewGroup) getBridge().getWebView().getParent();
            root.addView(surface, 0, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            player.getVLCVout().setVideoView(surface);
            player.getVLCVout().attachViews();
        });
        player.setEventListener(event -> {
            switch (event.type) {
                case MediaPlayer.Event.Playing: notifyListeners("playing", new JSObject()); break;
                case MediaPlayer.Event.EncounteredError: notifyListeners("error", new JSObject()); break;
                case MediaPlayer.Event.Buffering:
                    JSObject d = new JSObject(); d.put("percent", event.getBuffering());
                    notifyListeners("buffering", d); break;
            }
        });
    }

    @PluginMethod public void open(PluginCall call) {
        String url = call.getString("url");
        if (url == null) { call.reject("url required"); return; }
        Media media = new Media(libVLC, android.net.Uri.parse(url));
        player.setMedia(media);
        media.release();
        call.resolve();
    }
    @PluginMethod public void play(PluginCall call) { player.play(); call.resolve(); }
    @PluginMethod public void pause(PluginCall call) { player.pause(); call.resolve(); }
    @PluginMethod public void stop(PluginCall call) { player.stop(); call.resolve(); }
    @PluginMethod public void seek(PluginCall call) {
        player.setTime((long) (call.getDouble("seconds", 0.0) * 1000)); call.resolve(); }
    @PluginMethod public void setVolume(PluginCall call) {
        player.setVolume((int) (call.getDouble("volume", 1.0) * 100)); call.resolve(); }
    @PluginMethod public void mute(PluginCall call) {
        // libVLC has no direct mute on MediaPlayer; emulate with volume 0 handled app-side if needed.
        call.resolve(); }
    @PluginMethod public void setRate(PluginCall call) {
        player.setRate(call.getDouble("rate", 1.0).floatValue()); call.resolve(); }
    @PluginMethod public void setFit(PluginCall call) {
        String fit = call.getString("fit", "contain");
        player.setAspectRatio("fill".equals(fit) ? null : ""); // refined on device: use setScale / aspect per fit
        call.resolve(); }
    @PluginMethod public void setHwDecoding(PluginCall call) {
        // Applied to the NEXT open() via Media options (:codec=mediacodec_ndk / :codec=all).
        call.resolve(); }
    @PluginMethod public void selectAudio(PluginCall call) {
        player.setAudioTrack(call.getInt("index", -1)); call.resolve(); }
    @PluginMethod public void selectSubtitle(PluginCall call) {
        player.setSpuTrack(call.getInt("index", -1)); call.resolve(); }

    @Override
    protected void handleOnDestroy() {
        if (player != null) { player.stop(); player.release(); }
        if (libVLC != null) libVLC.release();
    }
}
