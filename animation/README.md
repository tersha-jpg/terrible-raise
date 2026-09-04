# float, air traffic control for merch (animation)

A 28-second looping animation that makes one argument: the merch supply chain is an
unmanaged tangle of handoffs, and float turns it into a single controlled airspace.

| Beat | Time | What is on screen |
| --- | --- | --- |
| Before | 0.0-5.4s | 33 suppliers, systems and channels scattered across the frame, wired together by dotted handoffs. Packets crawl between them; some stall amber. The counters are the ones nobody wants: handoffs, chasing emails, unreconciled lines. |
| Hand-over | 5.4-8.2s | float claims the airspace. Every label is pulled onto a flight-progress strip (`make` on the left, `move / sell / settle` on the right) and a radar scope opens with the float tower at its centre. |
| Routing | 8.8-20.8s | Traffic runs strip → scope → tower → scope → strip along cleared routes. float ai callouts fire: demand read live, a reorder raised early, two consignments sequenced onto one dock (one visibly held), stock reallocated, a settlement matched. |
| After | 20.8-24.4s | The scope collapses into four chips (176 partners, 8 systems, 4 channels, 4 ledgers) with one flow still running beneath them. |
| End card | 24.4-28.2s | float logo, the line, the terrible* mark. |

## Run it

```sh
python3 -m http.server 8000 --directory animation   # then open http://localhost:8000
```

Opening `index.html` off disk works too; `file://` blocks the Google Fonts request, so
body copy falls back to Helvetica/Arial. The display face (Helvetica Now Text) is local
and always loads.

## Controls

`Space` play/pause · `←` `→` scrub a second · `R` restart · `F` full-frame.

`F` (or opening `index.html#clean`) hides the controls and fills the window, which is the
mode to screen-record. The animation is a pure function of time, so scrubbing is exact
and every playback is identical.

## Recording it

`make-video.py` renders the timeline frame by frame in headless Chromium and encodes an
MP4, with no screen recorder and no dropped frames:

```sh
pip install playwright && python3 animation/make-video.py        # -> animation/dist/float-atc.mp4
```

## Slides

`make-slides.py` seeks the animation to the seven moments that carry the argument and
captures each at 1920x1080, so the deck is the same artwork as the film rather than a
redraw of it. It writes PNG masters, a PPTX with a speaker note on every slide, and a PDF:

```sh
pip install playwright python-pptx pillow
python3 animation/make-slides.py     # -> animation/dist/float-atc-slides.{pptx,pdf} + dist/slides/
```

The slide list, the moment each one freezes and its speaker note all live in `SLIDES` at
the top of that script. Slides are full-bleed images, so wording changes belong in
`index.html` and come through on the next run.

## Single file

```sh
python3 animation/build-artifact.py    # -> animation/dist/artifact.html
```

Fonts and logos inlined as data URIs, document wrapper stripped, so it can be published as
an Artifact or emailed as one file.

## Editing it

Everything lives in `index.html`, with no dependencies. The pieces worth knowing:

- `T`: the master timeline. Every scene alpha is derived from it, so moving a beat moves
  everything that hangs off it.
- `NODE_DATA`: the 33 labels and their sector. Add one and it appears in the tangle, on a
  strip, on the scope, and in the traffic schedule.
- `CAPTIONS`, `CALLOUTS`, `CHIPS`, `STATS`: all the copy, in one place near the top.
- `flights`: the deterministic schedule. Seeded, so the animation never differs run to run.
