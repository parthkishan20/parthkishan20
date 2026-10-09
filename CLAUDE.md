# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The GitHub profile README for `parthkishan20` (the special `<user>/<user>` repo). `README.md` renders on the GitHub profile page. There is no app, build, or test suite. The only code is a Python script that draws the README's images.

## Regenerating the terminal SVGs

Most of the README is six "terminal window" SVGs in `assets/terminal/`. They are generated, so don't hand-edit them. Change `scripts/terminal/gen_term.py` and re-run it:

```sh
# one-time setup
npm i jetbrains-mono
pip install fonttools brotli

# from the repo root
python3 scripts/terminal/gen_term.py node_modules/jetbrains-mono/fonts/webfonts assets/terminal
```

The script prints each window's name, height, and size in KB. `node_modules/` is only there for the font files and shouldn't be committed.

### How gen_term.py works

- Each window is a `win_*()` function that builds a `Win`, a character grid of `(char, color, bold)` cells. The functions use `prompt()`, `add()`, `put()`, `blank()`, and the `box()`/`harrow()` helpers. The `WINDOWS` list maps output filenames (`01-gh-fetch` … `06-contributions`) to these functions.
- `render()` turns the grid into `<text>`/`<tspan>` runs at fixed positions (`CW = 0.6 × font size`). Alignment only works because the font is monospaced.
- GitHub serves README SVGs as images, so they can't load web fonts. The script records every glyph used (`USED`), subsets JetBrains Mono NL Regular and Bold to only those glyphs, and embeds them as base64 WOFF in each SVG.
- `put()` throws if a line runs past `COLS` (window width 880px, about 112 columns) or if a character isn't in the font. When adding content, shorten or wrap the text (`wrap_words`) instead of widening the window.
- The colors come from the palette constants at the top of the script (`BG`, `GREEN`, `YEL`, …). Use these rather than new hex values.
- `06-contributions` is a static snapshot. You update it by hand by editing the `WEEKS` list (weekly counts), `MONTHS` (label offsets), and the hard-coded stats and "as of" date in `win_contrib()`.

## Keeping README and SVGs in sync

Each `<img>` in `README.md` has a long `alt` attribute that spells out all of the text in its SVG, for accessibility. Whenever you change the content of a `win_*` function, update the matching `alt` text too, so the facts (numbers, dates, project names) match exactly. The facts are repeated across windows as well. For example, the Refund Agent figures (9 scenarios, 46 assertions, 43 unit tests) appear in windows 02, 03, and 04, and the stack appears in 01 and 04.

Project links don't go inside the SVGs, because links in images don't work. They go in the markdown below each window (the `$ open --project` line and the `<details>` tables).

## GitHub Actions

`.github/workflows/contribution-graph.yml` runs every day, on pushes to `main`, and on manual dispatch. It generates a bomberman-style contribution graph with `abozanona/pacman-contribution-graph` and pushes it to the `output` branch. The current README doesn't embed that graph, since window 06 is the static contribution chart.
