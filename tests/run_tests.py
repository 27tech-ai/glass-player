#!/usr/bin/env python3
"""Glass Player — automated test suite (web engine).

Runs the REAL player in headless Chromium (Playwright) against local fixture
servers it starts itself. Every check prints PASS / FAIL / NOT TESTABLE.
Nothing here is mocked at the player level: parsing, proxy rules, settings and
playback are exercised through the shipped app.js.

Prerequisites: python3 + playwright + a Chromium build, ffmpeg (for fixtures).
Without ffmpeg the playback checks report NOT TESTABLE instead of failing.
Android/libVLC checks are NOT TESTABLE without an Android SDK + device and are
reported as such — see BUILD_ANDROID.md.

Usage:  python3 tests/run_tests.py
"""
import asyncio, json, os, shutil, subprocess, sys, tempfile, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = []

def report(name, ok, note=""):
    RESULTS.append((name, ok, note))
    print(f"{'PASS' if ok is True else 'FAIL' if ok is False else 'NOT TESTABLE'}  {name}  {note}")

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

class Cors(Quiet):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

def serve(directory, handler, port):
    srv = ThreadingHTTPServer(("127.0.0.1", port), lambda *a, **k: handler(*a, directory=directory, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

def make_fixtures(d):
    """Generate a tiny HLS + MP4 with ffmpeg. Returns False if ffmpeg is absent."""
    if not shutil.which("ffmpeg"):
        return False
    src = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
           "-f", "lavfi", "-i", "sine=frequency=440", "-t", "8"]
    subprocess.run(src + ["-c:v", "libx264", "-c:a", "aac", "-f", "hls", "-hls_time", "2",
                          os.path.join(d, "test.m3u8")], check=True)
    subprocess.run(src + ["-c:v", "libx264", "-c:a", "aac", os.path.join(d, "test.mp4")], check=True)
    with open(os.path.join(d, "list.m3u"), "w") as f:
        f.write("#EXTM3U\n#EXTINF:-1,Fixture HLS\nhttp://127.0.0.1:19098/test.m3u8\n"
                "#EXTINF:-1,Fixture MP4\nhttp://127.0.0.1:19098/test.mp4\n"
                "#EXTINF:-1,RTSP Cam\nrtsp://127.0.0.1:8554/cam\n")
    return True

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        report("playwright available", None, "pip install playwright — suite cannot run")
        return
    tmp = tempfile.mkdtemp(prefix="gp-fixtures-")
    have_media = make_fixtures(tmp)
    serve(ROOT, Quiet, 19099)          # the app itself
    if have_media: serve(tmp, Cors, 19098)
    APP = "http://127.0.0.1:19099/index.html"
    async with async_playwright() as pw:
        launch = {"args": ["--autoplay-policy=no-user-gesture-required", "--mute-audio"]}
        if os.environ.get("GP_CHROME"):  # optional: path to a Chromium/headless-shell binary
            launch["executable_path"] = os.environ["GP_CHROME"]
        browser = await pw.chromium.launch(**launch)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(APP); await page.wait_for_timeout(900)

        # --- M3U parser (real parseM3U from the shipped app.js) ---
        d = json.loads(await page.evaluate("""JSON.stringify((() => {
          const t1 = parseM3U('#EXTM3U\\n#EXTINF:-1 tvg-id="i1" group-title="News, World",Channel, One\\nhttp://x.tv/a.m3u8\\n');
          const t2 = parseM3U('\\uFEFF#EXTM3U\\r\\n#EXTGRP:Sport\\r\\n#EXTINF:-1,Bein\\r\\nhttp://x.tv/b.ts\\r\\n');
          const t3 = parseM3U('#EXTM3U\\n#EXTINF:-1,Rel\\nsub/l.m3u8\\n', 'http://h.tv/p/main.m3u');
          const t4 = parseM3U('#EXTM3U\\nhttp://x.tv/movies/My Film.mp4\\n');
          const t5 = parseM3U('#EXTM3U\\n#EXTINF:-1,A\\nhttp://x.tv/d.m3u8\\n#EXTINF:-1,A2\\nhttp://x.tv/d.m3u8\\n');
          return { n1: t1[0].name, g1: t1[0].group, rel: t3[0].url, bare: t4[0].name, grp: t2[0].group, dups: t5.length };
        })())"""))
        report("parser: quoted attrs + commas in name/group", d["n1"] == "Channel, One" and d["g1"] == "News, World")
        report("parser: BOM + CRLF + #EXTGRP", d["grp"] == "Sport")
        report("parser: relative URL resolution", d["rel"] == "http://h.tv/p/sub/l.m3u8")
        report("parser: bare URL naming", d["bare"] == "My Film")
        report("parser: duplicates removed", d["dups"] == 1)

        # --- proxy rules ---
        d2 = json.loads(await page.evaluate("""JSON.stringify((() => {
          localStorage.removeItem('gp-proxy');
          localStorage.setItem('gp-pub-proxy', JSON.stringify('0'));
          const off = proxiesFor('http://example.tv/x.m3u8').length;
          localStorage.setItem('gp-pub-proxy', JSON.stringify('1'));
          const on = proxiesFor('http://example.tv/x.m3u8').length;
          const lan = proxiesFor('http://192.168.1.5/x.m3u8').length;
          const alias = ipAlias('http://185.9.2.18:8080/a/b.m3u8');
          const twin = xtreamHlsUrl('http://h.tv/live/u/p/42.ts');
          return { off, on, lan, alias, twin };
        })())"""))
        report("proxies: public toggle off/on", d2["off"] == 0 and d2["on"] == 2)
        report("proxies: LAN never proxied", d2["lan"] == 0)
        report("ip alias: raw IP -> nip.io", d2["alias"] == "http://185.9.2.18.nip.io:8080/a/b.m3u8")
        report("xtream twin: .ts -> .m3u8", d2["twin"] == "http://h.tv/live/u/p/42.m3u8")

        # --- playback (needs ffmpeg fixtures) ---
        if not have_media:
            report("playback: HLS fixture", None, "ffmpeg not found")
            report("playback: MP4 fixture", None, "ffmpeg not found")
            report("protocol: RTSP honest fast error", None, "ffmpeg not found")
        else:
            await page.fill("#urlInput", "http://127.0.0.1:19098/list.m3u")
            await page.click("#loadUrlBtn")
            await page.wait_for_selector(".channel", state="attached", timeout=10000)
            for idx, name in [(0, "HLS"), (1, "MP4")]:
                await page.evaluate(f"document.querySelectorAll('.channel')[{idx}].click()")
                try:
                    await page.wait_for_function(
                        "() => { const v = document.querySelector('#video'); return v.currentTime > 0.3 && !v.paused; }",
                        timeout=20000)
                    report(f"playback: {name} fixture", True)
                except Exception:
                    report(f"playback: {name} fixture", False)
            await page.evaluate("document.querySelector('#channelsBtn').click()")
            await page.wait_for_timeout(300)
            await page.evaluate("document.querySelectorAll('.channel')[2].click()")
            try:
                await page.wait_for_function(
                    "() => (document.querySelector('#toast') || {}).textContent.includes('RTSP')", timeout=5000)
                report("protocol: RTSP honest fast error", True)
            except Exception:
                report("protocol: RTSP honest fast error", False)

        report("page errors during suite", len(errors) == 0, "; ".join(errors[:2]))
        report("android: libVLC bridge lifecycle", None, "needs Android SDK + device — see BUILD_ANDROID.md")
        await browser.close()
    bad = [r for r in RESULTS if r[1] is False]
    print(f"\n{sum(1 for r in RESULTS if r[1] is True)} PASS · {len(bad)} FAIL · "
          f"{sum(1 for r in RESULTS if r[1] is None)} NOT TESTABLE")
    sys.exit(1 if bad else 0)

asyncio.run(main())
