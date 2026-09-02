#!/usr/bin/env python3
"""Inline every local asset in index.html into one self-contained page.

Produces dist/artifact.html: the same site with fonts and images embedded as
data URIs and the document wrapper stripped, so it can be published as a
Claude Artifact (which supplies its own <!doctype>/<head>/<body>).

    python3 site/build-artifact.py
"""
import base64
import mimetypes
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "index.html"
OUT = HERE / "dist" / "artifact.html"

MIME = {".woff2": "font/woff2", ".webp": "image/webp", ".jpg": "image/jpeg"}


def data_uri(rel: str) -> str:
    path = HERE / rel
    mime = MIME.get(path.suffix) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    html = SRC.read_text()

    # video is left out of the artifact: a base64 data URI cannot be range-
    # requested, so it would defeat faststart and add megabytes to one page.
    # The demos degrade to their poster stills instead.
    html = re.sub(r'\s+data-(?:mp4-(?:lg|sm)|webm)="assets/video/[^"]*"', "", html)

    # font + images referenced as assets/...
    for rel in sorted({m for m in re.findall(r"assets/[\w./-]+", html)}):
        if rel.endswith(".txt") or rel.endswith((".mp4", ".webm")):
            continue
        html = html.replace(f"'{rel}'", f"'{data_uri(rel)}'")
        html = html.replace(f'"{rel}"', f'"{data_uri(rel)}"')

    # strip the document wrapper the artifact host provides
    html = re.sub(r"^.*?<title>", "<title>", html, flags=re.S)
    html = html.replace("</head>\n<body>\n", "", 1)
    html = re.sub(r"</body>\s*</html>\s*$", "", html)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"{OUT} — {len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
