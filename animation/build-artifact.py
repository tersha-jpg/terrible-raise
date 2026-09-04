#!/usr/bin/env python3
"""Inline every local asset in animation/index.html into one self-contained page.

Produces dist/artifact.html: the same animation with fonts and logos embedded as data
URIs and the document wrapper stripped, so it can be published as a Claude Artifact
(which supplies its own <!doctype>/<head>/<body>).

    python3 animation/build-artifact.py
"""
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
    html = SRC.read_text()
    for rel in sorted({m for m in re.findall(r"assets/[\w./-]+", html)}):
        uri = data_uri(rel)
        html = html.replace(f"'{rel}'", f"'{uri}'").replace(f'"{rel}"', f'"{uri}"')

    html = re.sub(r"^.*?<title>", "<title>", html, flags=re.S)
    html = html.replace("</head>\n<body>\n", "", 1)
    html = re.sub(r"</body>\s*</html>\s*$", "", html)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"{OUT} {len(html) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
