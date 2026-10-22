# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The GitHub profile README for `parthkishan20` (the special `<user>/<user>` repo). `README.md` renders on the GitHub profile page. It is plain markdown: no app, build, or test suite.

## Project links

`README.md` links to project repos under `github.com/parthkishan20/`. When a project repo is renamed, update its link here. GitHub redirects the old URL, but the link should point at the current name. Check the live names with `curl -s "https://api.github.com/users/parthkishan20/repos?per_page=100"`.

## Terminal SVGs (retired)

The README used to be built from six generated "terminal window" SVGs. The README was rewritten as plain text (commit `b917388`) and no longer embeds them, so the `terminal-svgs.yml` workflow was removed. It had been failing daily because `gen_term.py` exits when it can't find the `06-contributions.svg` `<img>` in `README.md`.

`scripts/terminal/gen_term.py` and `assets/terminal/` are kept for reference only. The script still expects that `<img>` in `README.md` and needs a GitHub token, so don't run it against the current README. To bring the SVG design back, restore the README from `34497cf` and re-add the workflow from the same commit.

## GitHub Actions

`.github/workflows/contribution-graph.yml` runs every day, on pushes to `main`, and on manual dispatch. It generates a bomberman-style contribution graph with `abozanona/pacman-contribution-graph` and pushes it to the `output` branch as `github-actions[bot]`. The current README doesn't embed that graph.
