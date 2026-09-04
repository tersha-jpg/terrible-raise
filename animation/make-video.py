#!/usr/bin/env python3
"""Render the animation frame by frame in headless Chromium and encode an MP4.

Deterministic: each frame is drawn by seeking the timeline, not by recording playback,
so nothing drops and the file is identical every run.

    pip install playwright
    python3 animation/make-video.py [--fps 30] [--width 1920] [--out animation/dist/float-atc.mp4]
"""
import argparse
import base64
import pathlib
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
]
FFMPEG_CANDIDATES = ["/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux"]


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
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    ffmpeg = find(FFMPEG_CANDIDATES, "ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg not found")
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    height = round(args.width * 9 / 16)

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        tmp = pathlib.Path(tmp)
        chrome = find(CHROME_CANDIDATES, "chromium")
        browser = pw.chromium.launch(executable_path=chrome)
        page = browser.new_page(viewport={"width": args.width, "height": height},
                                device_scale_factor=1)
        page.goto((HERE / "index.html").as_uri() + "#clean")
        page.wait_for_function("window.__floatAnim !== undefined", timeout=20000)
        page.wait_for_timeout(600)
        total = page.evaluate("window.__floatAnim.T.loop")
        frames = int(total * args.fps)
        print(f"{frames} frames at {args.fps}fps · {args.width}×{height}")
        for i in range(frames):
            page.evaluate(f"window.__floatAnim.seek({i / args.fps})")
            data = page.evaluate(
                "document.querySelector('#c').toDataURL('image/jpeg', 0.94)")
            (tmp / f"f{i:05d}.jpg").write_bytes(base64.b64decode(data.split(",", 1)[1]))
            if i % 60 == 0:
                print(f"  {i}/{frames}")
        browser.close()

        subprocess.run([ffmpeg, "-y", "-framerate", str(args.fps),
                        "-i", str(tmp / "f%05d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "18", "-preset", "slow",
                        "-vf", f"scale={args.width}:{height}", str(out)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{out} — {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
