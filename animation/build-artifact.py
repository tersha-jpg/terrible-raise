#!/usr/bin/env python3
"""Inline every local asset in animation/index.html into one self-contained page.

    python3 animation/build-artifact.py           # -> dist/artifact.html
    python3 animation/build-artifact.py --embed   # -> dist/embed.html

artifact.html has the document wrapper stripped, for publishing as a Claude Artifact
(the host supplies its own <!doctype>/<head>/<body>). embed.html is a complete page with
no controls, sized to fill whatever box it is dropped into, for an iframe on a website.
Both carry the fonts and logos as data URIs, so they are one file with no asset folder.
"""
import argparse
import base64
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "index.html"
OUT = HERE / "dist" / "artifact.html"
MIME = {".woff2": "font/woff2", ".webp": "image/webp"}


def data_uri(rel: str) -> str:
    path = HERE / rel
    mime = MIME.get(path.suffix, "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed", action="store_true",
                    help="build a standalone page for an iframe instead of an artifact")
    args = ap.parse_args()

    html = SRC.read_text()
    for rel in sorted({m for m in re.findall(r"assets/[\w./-]+", html)}):
        uri = data_uri(rel)
        html = html.replace(f"'{rel}'", f"'{uri}'").replace(f'"{rel}"', f'"{uri}"')

    out = OUT
    if args.embed:
        out = OUT.parent / "embed.html"
        # no controls, no letterboxing chrome: the animation fills the frame it is given
        html = html.replace('<body>', '<body class="clean">', 1)
        html = html.replace('</style>', """  html, body { height: 100%; overflow: hidden; }
  body.clean { padding: 0; background: var(--ink); }
  body.clean #stage { max-width: none; width: 100vw; height: 100vh; aspect-ratio: auto; }
</style>""", 1)
    else:
        html = re.sub(r"^.*?<title>", "<title>", html, flags=re.S)
        html = html.replace("</head>\n<body>\n", "", 1)
        html = re.sub(r"</body>\s*</html>\s*$", "", html)

    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f"{out} {len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
