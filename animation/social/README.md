# float social stills

Five boards, composed for portrait rather than cropped out of the 16:9 film. The strips
that run down the left and right of the animation cannot survive a portrait crop, so each
beat is rebuilt for the shape: the tangle as a portrait cloud, the scope centred with the
tower on it, the float ai findings as stacked cards, the after board as a 2x2 grid.

| Board | What it says |
| --- | --- |
| `s1-before` | The tangle. Hundreds of suppliers, disconnected systems, endless spreadsheets. |
| `s2-tower` | The scope and the tower. Air traffic control for merchandise. |
| `s3-ai` | Four float ai findings. float doesn't just watch, it routes and reacts. |
| `s4-after` | 176 partners, 8 systems, 4 channels, 4 ledgers. Every transaction, every data point, one tower. |
| `s5-end` | The mark and the line. A closer, or a profile grid tile. |

## Formats

One set of markup serves both, so the copy lives in exactly one place:

| Format | Size | Where it goes |
| --- | --- | --- |
| `feed/` | 1080 x 1350 | Instagram and LinkedIn feed, the 4:5 that takes the most vertical space in a scroll |
| `story/` | 1080 x 1920 | Stories and Reels covers, 9:16 |

Both are written as PNG (lossless, for reposting and for anyone placing them in a deck)
and JPEG at quality 94 (for upload). Boards render at 2x and are downscaled with Lanczos,
which is sharper than asking the browser for 1080 directly.

## Rebuild

```sh
pip install playwright pillow
python3 animation/social/make-social.py          # -> animation/dist/social/{feed,story}/
```

`index.html` is the source. Open it in a browser to see all five boards side by side;
add `class="story"` to `<body>` in the browser inspector to preview the 9:16 shape.

## Editing

- Copy: the `<h1>`, `.sub`, `.kicker` and card text, in place in `index.html`.
- Palette and type: `:root`.
- A new board: copy an `<article class="board" id="s6-...">`, and it gets shot in both
  formats automatically. The id becomes the filename.
- A square 1080 x 1080 for X or a LinkedIn carousel is one line: add
  `"square": (1080, 1080)` to `FORMATS` in `make-social.py`, plus a
  `body.square .board { height: 1080px }` rule.

## Before these go out

`s3-ai` and the figures on `s4-after` carry the same illustrative numbers as the film.
A still gets screenshotted and quoted, so swap them for real ones or soften the claims
before posting.
