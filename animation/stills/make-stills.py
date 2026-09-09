#!/usr/bin/env python3
"""Shoot the four 16:9 boards in animation/stills/index.html as PNGs.

Boards render at 2x and are downscaled with Lanczos, which is sharper than asking the
browser for 1920 directly. No logos on these boards: they are made for a deck that
carries its own branding.

    pip install playwright pillow
    python3 animation/stills/make-stills.py [--width 1920] [--scale 2]
"""
import argparse
import functools
import http.server
import pathlib
import socketserver
import threading

HERE = pathlib.Path(__file__).resolve().parent
CHROME = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
          "/opt/pw-browsers/chromium/chrome-linux/chrome"]


def chrome():
    import shutil
    for p in CHROME:
        if pathlib.Path(p).exists():
            return p
    return shutil.which("chromium")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--out-dir", default=str(HERE.parent / "dist" / "stills"))
    args = ap.parse_args()

    from PIL import Image
    from playwright.sync_api import sync_playwright

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = args.width, round(args.width * 9 / 16)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome())
        page = browser.new_page(viewport={"width": 2100, "height": 1300},
                                device_scale_factor=args.scale)
        page.goto(f"http://127.0.0.1:{port}/index.html")
        page.wait_for_timeout(1200)
        for board_id in page.eval_on_selector_all(".board", "els => els.map(e => e.id)"):
            raw = out_dir / f"{board_id}@{args.scale}x.png"
            # ids start with a digit, which is not a valid CSS id selector
            page.locator(f'[id="{board_id}"]').screenshot(path=str(raw))
            img = Image.open(raw).convert("RGB").resize((w, h), Image.LANCZOS)
            img.save(out_dir / f"{board_id}.png")
            raw.unlink()
            print(f"  {board_id}.png  {w}x{h}")
        browser.close()
    server.shutdown()
    print(out_dir)


if __name__ == "__main__":
    main()
