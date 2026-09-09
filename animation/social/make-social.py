#!/usr/bin/env python3
"""Shoot the portrait boards in animation/social/index.html as social stills.

Each board is captured twice, once as a 4:5 feed post and once as a 9:16 story, by
toggling the story class on <body>. Boards render at 2x and are downscaled with
Lanczos, which is sharper than asking the browser for 1080 directly.

    pip install playwright pillow
    python3 animation/social/make-social.py
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
FORMATS = {"feed": (1080, 1350), "story": (1080, 1920)}


def chrome():
    import shutil
    for p in CHROME:
        if pathlib.Path(p).exists():
            return p
    return shutil.which("chromium")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(HERE.parent / "dist" / "social"))
    ap.add_argument("--scale", type=int, default=2, help="render multiplier before downscale")
    args = ap.parse_args()

    from PIL import Image
    from playwright.sync_api import sync_playwright

    out_root = pathlib.Path(args.out_dir)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chrome())
        page = browser.new_page(viewport={"width": 1240, "height": 2100},
                                device_scale_factor=args.scale)
        page.goto(f"http://127.0.0.1:{port}/index.html")
        page.wait_for_timeout(1200)
        ids = page.eval_on_selector_all(".board", "els => els.map(e => e.id)")
        for fmt, (w, h) in FORMATS.items():
            page.evaluate(f"document.body.className = {fmt == 'story' and repr('story') or repr('')}")
            page.wait_for_timeout(400)
            out_dir = out_root / fmt
            out_dir.mkdir(parents=True, exist_ok=True)
            for board_id in ids:
                raw = out_dir / f"{board_id}@{args.scale}x.png"
                page.locator(f"#{board_id}").screenshot(path=str(raw))
                img = Image.open(raw).convert("RGB").resize((w, h), Image.LANCZOS)
                img.save(out_dir / f"{board_id}.png")
                img.save(out_dir / f"{board_id}.jpg", quality=94, subsampling=0, optimize=True)
                raw.unlink()
                print(f"  {fmt}/{board_id}.png  {w}x{h}")
        browser.close()
    server.shutdown()
    print(f"{out_root}")


if __name__ == "__main__":
    main()
