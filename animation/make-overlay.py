#!/usr/bin/env python3
"""Render the animation as a transparent overlay: titles only, alpha background.

Runs the same animation with #overlay, which drops the ground, the flight strips, the
HUD, the callouts, the kickers and every sub-line, leaving the white titles and the
artwork. Frames are captured with alpha and encoded for two destinations:

  float-atc-overlay.webm  VP9 with alpha, for a web page over any background. Small.
                          ffprobe reports yuv420p and ffmpeg's own decoder ignores the
                          alpha plane, but browsers composite it correctly.
  float-atc-overlay.mov   the editing master, in one of three codecs (--master):
                            png     PNG in QuickTime, lossless alpha, ~200 MB (default)
                            qtrle   QuickTime Animation, lossless alpha, ~214 MB
                            prores  ProRes 4444 with 16-bit alpha, ~1.07 GB

    pip install playwright
    python3 animation/make-overlay.py [--fps 30] [--width 1920]
                                      [--master png|qtrle|prores|none]
"""
import argparse
import base64
import functools
import http.server
import pathlib
import shutil
import socketserver
import subprocess
import threading

HERE = pathlib.Path(__file__).resolve().parent
CHROME = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
          "/opt/pw-browsers/chromium/chrome-linux/chrome"]
TITLE_FONT = HERE / "assets" / "title-font.woff2"


def chrome():
    for p in CHROME:
        if pathlib.Path(p).exists():
            return p
    return shutil.which("chromium")


def ffmpeg_binary():
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--out-dir", default=str(HERE / "dist"))
    ap.add_argument("--frames", default=None)
    ap.add_argument("--encode-only", action="store_true")
    ap.add_argument("--master", choices=["png", "qtrle", "prores", "none"], default="png",
                    help="codec for the editing master (default png, see the docstring)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    ffmpeg = ffmpeg_binary()
    if not ffmpeg:
        raise SystemExit("ffmpeg not found. pip install imageio-ffmpeg")
    if not TITLE_FONT.exists():
        print(f"note: {TITLE_FONT.name} is not present, so titles render in "
              f"Helvetica Now Text. Drop the licensed face in as that filename to use it.")

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    height = round(args.width * 9 / 16)
    frames_dir = pathlib.Path(args.frames or out_dir / "frames-overlay")
    frames_dir.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome())
        page = browser.new_page(viewport={"width": args.width, "height": height},
                                device_scale_factor=1)
        page.goto(f"http://127.0.0.1:{port}/index.html#overlay")
        page.wait_for_function("window.__floatAnim !== undefined", timeout=20000)
        page.wait_for_timeout(700)
        total = page.evaluate("window.__floatAnim.T.loop")
        frames = int(total * args.fps)
        print(f"{frames} frames at {args.fps}fps, {args.width}x{height}, alpha")
        for i in range(frames):
            if args.encode_only:
                break
            page.evaluate(f"window.__floatAnim.seek({i / args.fps})")
            # alpha survives an element screenshot with omit_background
            page.locator("#c").screenshot(path=str(frames_dir / f"f{i:05d}.png"),
                                          omit_background=True)
            if i % 60 == 0:
                print(f"  {i}/{frames}")
        browser.close()
    server.shutdown()

    seq = ["-framerate", str(args.fps), "-i", str(frames_dir / "f%05d.png")]
    codecs = {
        "png":    ["-c:v", "png", "-pred", "mixed"],
        "qtrle":  ["-c:v", "qtrle"],
        "prores": ["-c:v", "prores_ks", "-profile:v", "4444",
                   "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0"],
    }
    if args.master != "none":
        mov = out_dir / "float-atc-overlay.mov"
        subprocess.run([ffmpeg, "-y", *seq, *codecs[args.master], str(mov)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{mov} {mov.stat().st_size / 1e6:.1f} MB  ({args.master})")

    webm = out_dir / "float-atc-overlay.webm"
    subprocess.run([ffmpeg, "-y", *seq,
                    "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                    "-b:v", "0", "-crf", "28", "-row-mt", "1",
                    "-auto-alt-ref", "0",      # required, or VP9 drops the alpha plane
                    str(webm)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{webm} {webm.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
