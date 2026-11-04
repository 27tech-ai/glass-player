/* Glass Player — Android native engine bridge (libVLC via the Capacitor plugin "GlassVlc").
   On the web (GitHub Pages, any browser) this file is INERT: GPNative.available() returns
   false and the player uses its HTML5 / hls.js / mpegts.js engines exactly as before.
   Inside the Android app the plugin exposes libVLC, and app.js hands playback to it
   wholesale — that is how RTSP/UDP/AC3/MPEG-2 and everything else the web cannot decode
   gets played. See BUILD_ANDROID.md and android-plugin/GlassVlcPlugin.java. */
(function(){
  const cap = window.Capacitor;
  const plugin = () => (cap && cap.Plugins && cap.Plugins.GlassVlc) || null;
  let listened = false;
  function ensureListeners(p){
    if (listened || !p.addListener) return; listened = true;
    p.addListener('playing', () => dispatchEvent(new Event('gp-native-playing')));
    p.addListener('error', () => dispatchEvent(new Event('gp-native-error')));
  }
  const call = (m, args) => { const p = plugin(); if (!p) return Promise.reject(new Error('native unavailable')); ensureListeners(p); return p[m](args || {}); };
  window.GPNative = {
    available(){ try{ return !!(cap && cap.getPlatform && cap.getPlatform() === 'android' && plugin()); }catch{ return false; } },
    open(url){ return call('open', { url }); },
    play(){ return call('play'); },
    pause(){ return call('pause'); },
    stop(){ return call('stop'); },
    seek(seconds){ return call('seek', { seconds }); },
    setVolume(v){ return call('setVolume', { volume: v }); },        // 0..1
    mute(m){ return call('mute', { muted: !!m }); },
    setRate(r){ return call('setRate', { rate: r }); },
    setFit(f){ return call('setFit', { fit: f }); },                  // contain | cover | fill
    setHwDecoding(on){ return call('setHwDecoding', { enabled: !!on }); },
    selectAudio(i){ return call('selectAudio', { index: i }); },
    selectSubtitle(i){ return call('selectSubtitle', { index: i }); },
  };
})();
