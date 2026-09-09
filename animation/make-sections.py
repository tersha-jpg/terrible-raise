#!/usr/bin/env python3
"""Render the film on one flat colour and cut it into a film per section.

One render pass writes every frame; each section is then encoded out of that frame range,
with a short fade from and to the background colour so each film stands on its own.

    pip install playwright
    python3 animation/make-sections.py --bg 191919
"""
import argparse
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

# name, in, out (seconds on the film's own timeline)
SECTIONS = [
    ("01-before",              0.0,  6.3),
    ("02-air-traffic-control", 6.0, 12.7),
    ("03-float-ai",           12.6, 20.3),
    ("04-after",              20.2, 24.3),
    ("05-end-card",           24.1, 28.2),
]


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


def render(frames_dir, width, fps, bg):
    from playwright.sync_api import sync_playwright

    height = round(width * 9 / 16)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome())
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=1)
        page.goto(f"http://127.0.0.1:{port}/index.html?bg={bg}#clean")
        page.wait_for_function("window.__floatAnim !== undefined", timeout=20000)
        page.wait_for_timeout(800)
        total = page.evaluate("window.__floatAnim.T.loop")
        count = int(total * fps)
        print(f"{count} frames at {fps}fps, {width}x{height}, ground #{bg}")
        import base64
        for i in range(count):
            page.evaluate(f"window.__floatAnim.seek({i / fps})")
            data = page.evaluate("document.querySelector('#c').toDataURL('image/jpeg', 0.96)")
            (frames_dir / f"f{i:05d}.jpg").write_bytes(base64.b64decode(data.split(",", 1)[1]))
            if i % 120 == 0:
                print(f"  {i}/{count}")
        browser.close()
    server.shutdown()
    return count


def encode(ffmpeg, frames_dir, out, fps, start, end, bg, fade, crf):
    first = int(round(start * fps))
    n = max(int(round((end - start) * fps)), 1)
    dur = n / fps
    vf = (f"fade=t=in:st=0:d={fade}:color=0x{bg},"
          f"fade=t=out:st={max(dur - fade, 0):.3f}:d={fade}:color=0x{bg},"
          f"format=yuv420p")
    subprocess.run([ffmpeg, "-y", "-framerate", str(fps), "-start_number", str(first),
                    "-i", str(frames_dir / "f%05d.jpg"), "-frames:v", str(n),
                    "-vf", vf, "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
                    "-movflags", "+faststart", str(out)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  {out.name:34s} {dur:5.1f}s  {out.stat().st_size / 1e6:5.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default="191919", help="flat background colour, hex, no hash")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--fade", type=float, default=0.35)
    ap.add_argument("--end", type=float, default=24.4,
                    help="where the full film stops; 28.2 keeps the end card on it")
    ap.add_argument("--out-dir", default=str(HERE / "dist" / "sections"))
    ap.add_argument("--encode-only", action="store_true")
    args = ap.parse_args()

    ffmpeg = ffmpeg_binary()
    if not ffmpeg:
        raise SystemExit("ffmpeg not found. pip install imageio-ffmpeg")
    bg = args.bg.lstrip("#")
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    if not args.encode_only:
        render(frames_dir, args.width, args.fps, bg)

    print("encoding")
    for name, start, end in SECTIONS:
        encode(ffmpeg, frames_dir, out_dir / f"float-{name}.mp4",
               args.fps, start, end, bg, args.fade, args.crf)
    # the film ends on the after board: the end card is kept as its own clip, for later
    encode(ffmpeg, frames_dir, out_dir / "float-full-film.mp4",
           args.fps, 0.0, args.end, bg, args.fade, args.crf)
    print(out_dir)


if __name__ == "__main__":
    main()
