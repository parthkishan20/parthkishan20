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

# from the repo root; needs a GitHub token for the contribution data
GITHUB_TOKEN=<token> python3 scripts/terminal/gen_term.py node_modules/jetbrains-mono/fonts/webfonts assets/terminal
```

The script prints each window's name, height, and size in KB. `node_modules/` is only there for the font files and shouldn't be committed.

### How gen_term.py works

- Each window is a `win_*()` function that builds a `Win`, a character grid of `(char, color, bold)` cells. The functions use `prompt()`, `add()`, `put()`, `blank()`, and the `box()`/`harrow()` helpers. The `WINDOWS` list maps output filenames (`01-gh-fetch` … `06-contributions`) to these functions.
- `render()` turns the grid into `<text>`/`<tspan>` runs at fixed positions (`CW = 0.6 × font size`). Alignment only works because the font is monospaced.
- GitHub serves README SVGs as images, so they can't load web fonts. The script records every glyph used (`USED`), subsets JetBrains Mono NL Regular and Bold to only those glyphs, and embeds them as base64 WOFF in each SVG.
- `put()` throws if a line runs past `COLS` (window width 880px, about 112 columns) or if a character isn't in the font. When adding content, shorten or wrap the text (`wrap_words`) instead of widening the window.
- The colors come from the palette constants at the top of the script (`BG`, `GREEN`, `YEL`, …). Use these rather than new hex values.
- `06-contributions` is built from live data. `fetch_contrib()` calls the GitHub GraphQL API for the profile's last-year calendar and per-year totals, and `contrib_stats()` works out the streak, active days, peak day and busiest week. The script also rewrites that window's `alt` text in `README.md`, so don't edit that `alt` by hand.
- The output is byte-identical between runs with the same data (the font is saved with `recalcTimestamp=False`). That's what lets the workflow skip committing when nothing changed.

## Keeping README and SVGs in sync

Each `<img>` in `README.md` has a long `alt` attribute that spells out all of the text in its SVG, for accessibility. Whenever you change the content of windows 01–05, update the matching `alt` text too, so the facts (numbers, dates, project names) match exactly. The facts are repeated across windows as well. For example, the Refund Agent figures (9 scenarios, 46 assertions, 43 unit tests) appear in windows 02, 03, and 04, and the stack appears in 01 and 04.

Project links don't go inside the SVGs, because links in images don't work. They go in the markdown below each window (the `$ open --project` line and the `<details>` tables).

## GitHub Actions

`.github/workflows/terminal-svgs.yml` runs every day at 06:00 UTC, on manual dispatch, and on pushes to `main` that touch `scripts/terminal/` or the workflow itself. It installs pinned versions of `jetbrains-mono` and `fonttools`, regenerates all six SVGs using the built-in `GITHUB_TOKEN`, and commits `assets/terminal/` and `README.md` back to `main` as `github-actions[bot]` only if they changed. Because of these commits, pull before you push.

`.github/workflows/contribution-graph.yml` runs every day, on pushes to `main`, and on manual dispatch. It generates a bomberman-style contribution graph with `abozanona/pacman-contribution-graph` and pushes it to the `output` branch. The current README doesn't embed that graph, since window 06 already shows contributions.
