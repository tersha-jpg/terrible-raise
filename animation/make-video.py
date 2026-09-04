#!/usr/bin/env python3
"""Render the animation frame by frame in headless Chromium and encode an MP4.

Deterministic: each frame is drawn by seeking the timeline, not by recording playback,
so nothing drops and the file is identical every run.

    pip install playwright
    python3 animation/make-video.py [--fps 30] [--width 1920] [--out animation/dist/float-atc.mp4]
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
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
]
# Playwright's bundled ffmpeg is a stripped build with no libx264, so it is a last resort
FFMPEG_CANDIDATES: list[str] = []


def ffmpeg_binary():
    for p in FFMPEG_CANDIDATES:
        if pathlib.Path(p).exists():
            return p
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()   # pip install imageio-ffmpeg
    except ImportError:
        return None


def find(paths, fallback):
    for p in paths:
        if pathlib.Path(p).exists():
            return p
    return shutil.which(fallback)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--out", default=str(HERE / "dist" / "float-atc.mp4"))
    ap.add_argument("--frames", default=None, help="where to keep the rendered frames")
    ap.add_argument("--encode-only", action="store_true",
                    help="skip rendering and encode the frames already on disk")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    ffmpeg = ffmpeg_binary()
    if not ffmpeg:
        raise SystemExit("ffmpeg not found: pip install imageio-ffmpeg")
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    height = round(args.width * 9 / 16)

    # serve the folder so the canvas stays same-origin (file:// taints it)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    frames_dir = pathlib.Path(args.frames or out.parent / "frames")
    frames_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        tmp = frames_dir
        chrome = find(CHROME_CANDIDATES, "chromium")
        browser = pw.chromium.launch(executable_path=chrome)
        page = browser.new_page(viewport={"width": args.width, "height": height},
                                device_scale_factor=1)
        page.goto(f"http://127.0.0.1:{port}/index.html#clean")
        page.wait_for_function("window.__floatAnim !== undefined", timeout=20000)
        page.wait_for_timeout(600)
        total = page.evaluate("window.__floatAnim.T.loop")
        frames = int(total * args.fps)
        print(f"{frames} frames at {args.fps}fps · {args.width}×{height}")
        for i in range(frames):
            if args.encode_only:
                break
            page.evaluate(f"window.__floatAnim.seek({i / args.fps})")
            # same-origin over http, so the canvas exports directly: far faster
            # than an element screenshot per frame
            data = page.evaluate("document.querySelector('#c').toDataURL('image/jpeg', 0.95)")
            (tmp / f"f{i:05d}.jpg").write_bytes(base64.b64decode(data.split(",", 1)[1]))
            if i % 60 == 0:
                print(f"  {i}/{frames}")
        browser.close()

    subprocess.run([ffmpeg, "-y", "-framerate", str(args.fps),
                    "-i", str(frames_dir / "f%05d.jpg"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", "-preset", "slow",
                    "-vf", f"scale={args.width}:{height}", str(out)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    server.shutdown()
    print(f"{out} {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
