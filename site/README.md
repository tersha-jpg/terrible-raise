# float by terrible* - investor site

A one-page investor site built from the **float by terrible\* pitch deck (September 2026)**
(`float by terrible | pitch deck | September 2026.pdf` in Drive). All twelve slides, in
order, re-set for scrolling on a phone or a laptop instead of a 16:9 projector.

It follows the deck's design language: near-black ground with grain, the `terrible*` blue,
figures set between thin blue rules, square-cornered panels, Archivo for copy and Helvetica
Now Text for display. House style is no em dashes anywhere, hyphens only.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The site. All CSS and JS inline; no build step, no dependencies. |
| `assets/img/` | Photography, product shots, portraits, logos, and the two float UI screenshots lifted from the September deck. |
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

It is a static page - any host will do (Netlify, Vercel, GitHub Pages, Cloudflare
Pages, S3). Publish the contents of `site/` at the web root. Two things to set once
a domain exists:

- `og:image` in `index.html` needs an absolute URL for link previews to render.
- The `Request the deck` buttons are `mailto:tersha@terrible.group` links, copying
  `rich@terrible.group`. Swap them for a form or a data-room link to gate the deck.

## Single-file build

```sh
python3 site/build-artifact.py   # -> site/dist/artifact.html (~0.5 MB)
```

Everything is embedded as data URIs, so the result can be emailed, dropped into a
data room, or published as an Artifact with no accompanying asset folder.

## Keeping it in step with the deck

Copy and figures come from the September 2026 PDF deck, not from the `../stories/*.dc.html`
boards, which are still at the August 2026 version. Nothing syncs any of the three, so a
change to the deck needs the same edit made here by hand.

Section numbering follows the deck: The Business and Our Clients carry no number, and the
count runs 01 The Market to 09 The Ask. The deck itself skips 05 between Traction and The
Platform; the site numbers straight through.
