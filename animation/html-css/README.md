# float control tower, in HTML and CSS

The same 28-second piece as `../index.html`, rebuilt without canvas and without
JavaScript. Every word on screen is real text in the markup, every movement is a CSS
animation, and the whole thing is one file plus four assets.

## Why this version exists

| | canvas version | this version |
| --- | --- | --- |
| Editing copy | in a JS table, redraws on load | in the HTML, in place |
| Text | pixels | real text: selectable, searchable, readable by a screen reader |
| Styling | numbers in JS | CSS variables and rules a front-end dev can own |
| Motion | every frame computed | CSS keyframes, cheap for the browser |
| Density | ~100 scheduled flights, per-frame trails | 12 routes, staged callouts |

The canvas version is still the master for video export, because it is frame-accurate.
This one is the master for a web page.

## Drop it on a site

```html
<iframe src="/float/html-css/index.html"
        title="float, air traffic control for merchandise"
        loading="lazy"
        style="width:100%; aspect-ratio:16/9; border:0; display:block"></iframe>
```

Or paste the `<style>` block and the `.stage` markup straight into a page and skip the
iframe. Nothing in it is global except the two `@font-face` rules and `:root`.

## How it is built

- `.stage` is a container (`container-type: size`) and everything inside is sized in
  `cqw`, where `1cqw` is 1% of the stage width. The composition scales with its box, at
  any width, with no media queries and no JavaScript.
- `--loop` on `.stage` is the length of the whole piece. Every scene is a percentage of
  it, so retiming the film is one number plus the `@keyframes` percentages.
- The four `.scene` sections cross-fade: before, control, after, end card.
- Traffic is a stroke trick: each route is drawn twice, once faint and once as a short
  dash with `stroke-dasharray`, animated along the path with `stroke-dashoffset`. Each
  packet path carries `pathLength="1000"`, so every route takes the same time to fly
  whatever its real length.
- The radar sweep is a rotating `conic-gradient`. Its centring translate sits inside the
  same `transform` as the rotation on purpose: the standalone `rotate` property composes
  outside `transform`, which swings the circle around the stage instead of spinning it
  in place.
- `prefers-reduced-motion` holds the after board rather than looping.

## Editing

- Copy: the `<h2>`, `<p>` and `<li>` text, in place.
- Palette and type: `:root`.
- Beats and their timing: the `@keyframes scene-*` percentages.
- Panels, chips and callouts: plain HTML, add or remove rows freely.

## The one thing it does not do

The composition is fixed, like a video frame: on a narrow phone the whole board scales
down rather than reflowing into a column. If you need a phone-specific layout, treat this
as the desktop asset and give mobile the video, or add a `@media (max-width: 640px)` block
that hides `.panel` and enlarges `.caption`.
