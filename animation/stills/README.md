# float stills, 16:9

Four 1920 x 1080 PNGs, no logos: copy on the left, art on the right. Made for dropping
into a deck that carries its own branding, and for anywhere a slide-shaped still is
wanted instead of the film.

| File | The point |
| --- | --- |
| `01-before.png` | The tangle. Hundreds of suppliers, disconnected systems, endless spreadsheets. |
| `02-tower.png` | The scope, with the tower at its centre. Air traffic control for merchandise. |
| `03-ai.png` | Four float ai findings. It doesn't just watch, it routes and reacts. |
| `04-after.png` | 176 partners, 8 systems, 4 channels, 4 ledgers. |

No float or terrible* mark anywhere, so `02-tower` labels its hub **Tower / Control**
in type rather than sitting the wordmark in the middle of the scope. If you want the
mark back on that board, replace the `.hub-label` markup with the logo `<img>`.

## Rebuild

```sh
pip install playwright pillow
python3 animation/stills/make-stills.py                 # -> animation/dist/stills/*.png
python3 animation/stills/make-stills.py --width 3840    # same boards at 4K
```

Boards render at 2x and are downscaled with Lanczos, which is sharper than asking the
browser for 1920 directly.

## Editing

- Copy: the `<h1>`, `.sub` and `.kicker` text, in place in `index.html`.
- Palette and type: `:root`.
- A fifth board: copy an `<article class="board" id="05-...">` and it is picked up
  automatically. The id becomes the filename.
- The board ids start with a digit, so the renderer selects them with `[id="..."]`
  rather than `#...`, which is not a valid CSS id selector.

## Before these go out

`03-ai` and the figures on `04-after` carry the same illustrative numbers as the film.
Swap them for real ones before anything is presented or posted.
