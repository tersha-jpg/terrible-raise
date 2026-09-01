# float by terrible* — investor site

A one-page investor site built from the **float by terrible\* pitch deck (September 2026)**.
Same eleven stories as the deck, same design language (near-black ground, Archivo +
Helvetica Now Text, the `terrible*` blue and asterisk), re-set for scrolling on a phone
or a laptop instead of 1080 × 1920 boards.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The site. All CSS and JS inline; no build step, no dependencies. |
| `assets/img/` | Photography, product shots and logos, copied from `../stories/`. |
| `assets/fonts/` | Helvetica Now Text (Bold), the subset the deck itself embeds. |
| `build-artifact.py` | Inlines every asset into `dist/artifact.html` for publishing as a single file. |

## Run it locally

```sh
python3 -m http.server 8000 --directory site
# then open http://localhost:8000
```

Opening `index.html` directly off disk works too, though `file://` blocks the
Google Fonts request, so body copy falls back to Helvetica/Arial.

## Deploy

It is a static page — any host will do (Netlify, Vercel, GitHub Pages, Cloudflare
Pages, S3). Publish the contents of `site/` at the web root. Two things to set once
a domain exists:

- `og:image` in `index.html` needs an absolute URL for link previews to render.
- The `Request the deck` buttons are `mailto:rich@terrible.group` links. Swap them
  for a form or a data-room link if you want to gate the deck.

## Single-file build

```sh
python3 site/build-artifact.py   # -> site/dist/artifact.html (~0.5 MB)
```

Everything is embedded as data URIs, so the result can be emailed, dropped into a
data room, or published as an Artifact with no accompanying asset folder.

## Keeping it in step with the deck

Copy and figures come from the twelve `../stories/*.dc.html` boards. When a board
changes, the matching section here needs the same edit — the numbers appear in both
places and nothing syncs them automatically.
