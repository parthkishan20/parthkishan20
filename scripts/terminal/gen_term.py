"""Generate terminal-window SVGs for Parth's GitHub profile README.

Setup (once):
    npm i jetbrains-mono
    pip install fonttools brotli
Run from the repo root:
    python3 scripts/terminal/gen_term.py node_modules/jetbrains-mono/fonts/webfonts assets/terminal
Edit the content in each win_* function (and WEEKS for the contribution window),
then re-run to redraw the SVGs. The font is subset and embedded, because SVG
images on GitHub cannot load web fonts.
"""
import base64, io, math, os, sys
from html import escape
from fontTools.ttLib import TTFont
from fontTools import subset

FONT_DIR, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FONT_FILES = {400: f"{FONT_DIR}/JetBrainsMonoNL-Regular.woff2", 700: f"{FONT_DIR}/JetBrainsMonoNL-Bold.woff2"}
CMAP = TTFont(FONT_FILES[400]).getBestCmap()

# ---------- terminal palette ----------
BG, BAR, EDGE = "#0c0f0d", "#161b17", "#27302a"
FG, DIM, WHITE = "#c9d6cc", "#6f7d73", "#eef4ef"
GREEN, YEL, BLUE, MAG, CYAN, RED = "#46d18b", "#f3c969", "#6aa8f0", "#c678dd", "#56c2c6", "#e86b6b"
G1, G2, G3 = "#24573c", "#2f8a5b", "#46d18b"   # contribution greens, low to high

W = 880
SIZE = 13
CW = SIZE * 0.6            # JetBrains Mono advance = 600/1000 em
LH = SIZE * 1.32           # ascent + descent, so box-drawing glyphs join up
PADX, BAR_H, PADY = 22, 34, 16
COLS = int((W - 2 * PADX) // CW)
USED = {400: set(), 700: set()}

class Win:
    def __init__(self, title):
        self.title, self.rows, self.carets = title, [], []
    def _row(self, r):
        while len(self.rows) <= r: self.rows.append({})
        return self.rows[r]
    def put(self, r, c, text, color=FG, bold=False):
        row = self._row(r)
        for i, ch in enumerate(text):
            if ord(ch) not in CMAP and ch != " ":
                raise ValueError(f"missing glyph {ch!r}")
            if c + i >= COLS: raise ValueError(f"line too long ({c + i} >= {COLS}): {text!r}")
            row[c + i] = (ch, color, bold)
    def add(self, *spans):
        r, c = len(self.rows), 0
        self._row(r)
        for sp in spans:
            if isinstance(sp, str): sp = (sp,)
            text, color, bold = (tuple(sp) + (FG, False)[len(sp) - 1:])[:3]
            self.put(r, c, text, color, bold); c += len(text)
        return r
    def blank(self, n=1):
        for _ in range(n): self._row(len(self.rows))
    def prompt(self, cmd="", path="~", caret=False):
        r = self.add(("parth@github", GREEN, True), (":", FG), (path, BLUE, True), ("$ ", FG), (cmd, WHITE))
        if caret: self.carets.append((r, len("parth@github:") + len(path) + 2 + len(cmd)))
        return r

def S(text, color=FG, bold=False):
    return (text, color, bold)

def render(win):
    H = int(BAR_H + PADY * 2 + len(win.rows) * LH)
    o = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{EDGE}"/>',
         f'<path d="M0.5 {BAR_H} V12.5 a12 12 0 0 1 12 -12 H{W - 12.5} a12 12 0 0 1 12 12 V{BAR_H}Z" fill="{BAR}" stroke="{EDGE}"/>']
    for i in range(3):
        o.append(f'<circle cx="{20 + i * 17}" cy="{BAR_H / 2}" r="5.5" fill="#3a433d"/>')
    o.append(f'<text x="{W / 2}" y="{BAR_H / 2 + 4.5}" text-anchor="middle" class="t" fill="{DIM}" font-size="12">{escape(win.title)}</text>')
    USED[400].update(win.title)
    asc = SIZE * 1.02
    for r, row in enumerate(win.rows):
        if not row: continue
        y = BAR_H + PADY + r * LH + asc
        cols = sorted(row)
        runs, cur = [], None
        for c in range(cols[0], cols[-1] + 1):
            ch, color, bold = row.get(c, (" ", None, False))
            if ch == " " and cur and cur["color"] is not None:
                cur["text"] += " "; continue
            style = (color, bold)
            if cur is None or (cur["color"], cur["bold"]) != style:
                if cur: runs.append(cur)
                cur = {"c": c, "text": ch, "color": color, "bold": bold}
            else:
                cur["text"] += ch
        if cur: runs.append(cur)
        spans = []
        for run in runs:
            t = run["text"].rstrip()
            if not t.strip() or run["color"] is None: continue
            USED[700 if run["bold"] else 400].update(t)
            fw = ' font-weight="700"' if run["bold"] else ""
            spans.append(f'<tspan x="{PADX + run["c"] * CW:.2f}" fill="{run["color"]}"{fw}>{escape(t)}</tspan>')
        o.append(f'<text y="{y:.2f}" class="t" xml:space="preserve">{"".join(spans)}</text>')
    for r, c in win.carets:
        y = BAR_H + PADY + r * LH + 1
        o.append(f'<rect class="caret" x="{PADX + c * CW:.2f}" y="{y:.2f}" width="{CW - 0.5:.2f}" height="{LH - 2:.2f}" fill="{GREEN}"/>')
    return H, "".join(o)

# ======================================================================
# 01 · gh-fetch (neofetch-style header)
# ======================================================================
def win_fetch():
    w = Win("parth@github: ~")
    w.prompt("gh-fetch parthkishan20")
    w.blank()
    logo = ["██████▄ ", "██   ▀██", "██    ██", "██   ▄██", "██████▀ ", "██      ", "██      ", "██      "]
    info = [
        [S("parthkishan20", YEL, True), S("@", DIM), S("github", YEL, True)],
        [S("─" * 34, DIM)],
        [S("Name", GREEN, True), S(":      Parthkumar Patel")],
        [S("Role", GREEN, True), S(":      "), S("AI/GenAI + Full-Stack Engineer", WHITE, True)],
        [S("Education", GREEN, True), S(": MS Computer Science · Stevens '26 · GPA 3.9")],
        [S("Location", GREEN, True), S(":  NJ / NYC metro · open to remote")],
        [S("Status", GREEN, True), S(":    "), S("● actively interviewing", YEL, True)],
        [S("Seeking", GREEN, True), S(":   SWE · Full Stack · Frontend · AI/GenAI")],
        [S("About", GREEN, True), S(":     LLM features that behave the same in CI as in the demo")],
        [S("Frontend", GREEN, True), S(":  TypeScript · React · Next.js")],
        [S("Backend", GREEN, True), S(":   Python · FastAPI")],
        [S("AI", GREEN, True), S(":        Anthropic API · LiteLLM · SSE streaming")],
        [S("Data", GREEN, True), S(":      PostgreSQL · Supabase")],
        [S("Ship", GREEN, True), S(":      Docker · Playwright")],
        [S("Contact", GREEN, True), S(":   parthkishan20@gmail.com")],
        [],
    ]
    start = len(w.rows)
    for i in range(max(len(logo), len(info) + 1)):
        w._row(start + i)
    for i, ln in enumerate(logo):
        w.put(start + 2 + i, 2, ln, GREEN, True)
    ic = 16
    for i, spans in enumerate(info):
        c = ic
        for text, color, bold in spans:
            w.put(start + i, c, text, color, bold); c += len(text)
    sw = [("#1b1f1c"), RED, GREEN, YEL, BLUE, MAG, CYAN, FG]
    r = start + len(info)
    w._row(r)
    for k, col in enumerate(sw):
        w.put(r, ic + k * 3, "███", col)
    w.blank()
    w.prompt(caret=True)
    return w

# ======================================================================
# 02 · proof table
# ======================================================================
def wrap_words(text, width):
    out, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if len(t) <= width or not cur: cur = t
        else: out.append(cur); cur = word
    if cur: out.append(cur)
    return out

def win_proof():
    w = Win("parth@github: ~/projects")
    w.prompt("proof --top 4", "~/projects")
    w.blank()
    widths = [2, 22, 34, 33]
    heads = ["#", "PROJECT", "WHAT IT SHOWS", "NUMBERS"]
    def border(l, m, r):
        return l + m.join("─" * (x + 2) for x in widths) + r
    total = len(border("┌", "┬", "┐"))
    assert total <= COLS, total
    w.add(S(border("┌", "┬", "┐"), DIM))
    r = w.add(S("│", DIM))
    c = 1
    for wd, h in zip(widths, heads):
        w.put(r, c + 1, h, CYAN, True); c += wd + 3; w.put(r, c - 1, "│", DIM)
    w.add(S(border("├", "┼", "┤"), DIM))
    rows = [
        ("01", [("Refund Agent", WHITE, True), ("[demo]", CYAN, False), ("Next.js · Anthropic", DIM, False)],
         "Agent guardrails in code: every tool call passes one rule gate",
         [("$900 refund blocked with no system prompt", YEL, True), ("9 scenarios · 46 assertions · 43 unit tests", FG, False)]),
        ("02", [("AI Resume Tailoring", WHITE, True), ("Platform", WHITE, True), ("FastAPI · LiteLLM", DIM, False)],
         "LLM product with SSE streaming, provider-agnostic models and a mock mode for CI",
         [("23 REST/SSE endpoints", YEL, True), ("89 unit + 13 Playwright E2E tests", FG, False)]),
        ("03", [("Ledger", WHITE, True), ("[live]", CYAN, False), ("React 19 · Supabase", DIM, False)],
         "Real-time shared-expense PWA, built test-first, that replaced a 3-person spreadsheet",
         [("< 2 s cross-device sync", YEL, True), ("193 Vitest · 48 pgTAP · Lighthouse a11y 100", FG, False)]),
        ("04", [("Financial QA Bot", WHITE, True), ("Python · OpenRouter", DIM, False)],
         "Natural-language questions over financial CSVs, LLM + rule-based fallback",
         [("automated reports · ratio analysis", FG, False)]),
    ]
    for i, (num, proj, what, nums) in enumerate(rows):
        cells = [[(num, YEL, True)], proj,
                 [(ln, FG, False) for ln in wrap_words(what, widths[2])],
                 [piece for t, col, b in nums for piece in [(ln, col, b) for ln in wrap_words(t, widths[3])]]]
        height = max(len(x) for x in cells)
        for k in range(height):
            r = w.add(S("│", DIM))
            c = 1
            for wd, cell in zip(widths, cells):
                if k < len(cell):
                    t, col, b = cell[k]
                    w.put(r, c + 1, t, col, b)
                c += wd + 3
                w.put(r, c - 1, "│", DIM)
        if i < len(rows) - 1:
            w.add(S(border("├", "┼", "┤"), DIM))
    w.add(S(border("└", "┴", "┘"), DIM))
    w.add(S("4 rows · links to each project are under this window ↓", DIM))
    return w

# ======================================================================
# 03 · rule gate diagram + eval summary
# ======================================================================
def box(w, r0, c0, width, height, lines, color=FG, dash=False):
    h_, v_ = ("╌", "╎") if dash else ("─", "│")
    w.put(r0, c0, "┌" + h_ * (width - 2) + "┐", color)
    for k in range(1, height - 1):
        w.put(r0 + k, c0, v_, color); w.put(r0 + k, c0 + width - 1, v_, color)
    w.put(r0 + height - 1, c0, "└" + h_ * (width - 2) + "┘", color)
    for k, (t, col, b) in enumerate(lines):
        w.put(r0 + 1 + k, c0 + 2, t, col, b)

def harrow(w, r, c0, c1, label="", color=DIM):
    n = c1 - c0
    body = "─" * (n - 1) + "▶"
    if label:
        lab = f" {label} "
        s = (n - len(lab)) // 2
        body = "─" * s + lab + "─" * (n - 1 - s - len(lab)) + "▶"
    w.put(r, c0, body, color)
    if label:
        s = (n - len(f" {label} ")) // 2
        w.put(r, c0 + s + 1, label, FG)

def win_gate():
    w = Win("parth@github: ~/refund-agent")
    w.prompt("cat rule-gate.txt", "~/refund-agent")
    w.blank()
    base = len(w.rows)
    for _ in range(13): w._row(len(w.rows))
    R = lambda k: base + k
    # boxes
    box(w, R(2), 11, 17, 5, [("agent loop", WHITE, True), ("streaming", DIM, False), ("Anthropic API", DIM, False)])
    box(w, R(3), 46, 13, 3, [("RULE GATE", YEL, True)], YEL)
    box(w, R(2), 77, 28, 5, [("tools", WHITE, True), ("refund · store credit", FG, False), ("+ 2 other tools", DIM, False)])
    # customer
    w.put(R(3), 0, "customer", FG, True)
    w.put(R(4), 0, "message", DIM)
    w.put(R(4), 8, "─▶", DIM)
    # arrows on the middle row
    harrow(w, R(4), 28, 46, "tool request")
    harrow(w, R(4), 59, 77, "within policy")
    # result path back to the loop
    w.put(R(0), 19, "┌" + "─" * (90 - 20) + "┐", DIM)
    lab = " result returned to model "
    s = 19 + (90 - 19 - len(lab)) // 2
    w.put(R(0), s, lab, FG)
    w.put(R(1), 19, "▼", DIM)
    w.put(R(1), 90, "│", DIM)
    w.put(R(2), 90, "┴", DIM)
    # violates policy branch
    w.put(R(5), 52, "┬", YEL)
    w.put(R(6), 52, "│", DIM); w.put(R(6), 54, "violates policy", FG)
    w.put(R(7), 52, "▼", DIM)
    box(w, R(8), 43, 19, 4, [("BLOCKED", RED, True), ("no side effect", FG, False)], RED, dash=True)
    w.put(R(9), 0, "$900 refund, system", YEL, True)
    w.put(R(10), 0, "prompt deleted ──────────────────▶", YEL)
    w.put(R(10), 34, "────────▶", YEL)
    w.blank()
    w.prompt("cat eval-summary.txt", "~/refund-agent")
    for k, v, col in [("scenarios", "9", FG), ("assertions", "46", FG), ("unit tests", "43", FG),
                      ("model modes", "live · scripted · recorded", FG)]:
        w.add(S(f"{k} ".ljust(16, "."), DIM), S(" " + v, col, True))
    w.add(S("headline ".ljust(16, "."), DIM), S(" $900 refund, no system prompt ", YEL, True), S("──▶ ", DIM),
          S("BLOCKED AT GATE ", RED, True), S("✓", GREEN, True))
    w.add(S("note ".ljust(16, "."), DIM), S(" four tools, incl. a deliberately confusable refund / store-credit pair", FG))
    return w

# ======================================================================
# 04 · rules + stack
# ======================================================================
def win_rules():
    w = Win("parth@github: ~")
    w.prompt("cat ~/.llm-rules")
    w.add(S("# how I ship LLM features", DIM))
    rules = [("policy lives in code, not in the prompt", "refund agent rule gate"),
             ("model calls are replayable for CI", "resume platform mock mode · refund agent recorded runs"),
             ("evaluate from traces", "refund agent: 9 scenarios, 46 assertions"),
             ("never render raw model output", "resume platform PDF → YAML normalizer")]
    for i, (rule, ref) in enumerate(rules, 1):
        w.add(S(f"{i}  ", YEL, True), S(rule.ljust(42), WHITE), S("# " + ref, DIM))
    w.blank()
    w.prompt("cat stack.toml")
    for k, vals in [("frontend", ["TypeScript", "React", "Next.js"]), ("backend", ["Python", "FastAPI"]),
                    ("ai", ["Anthropic API", "LiteLLM"]), ("data", ["PostgreSQL", "Supabase"]),
                    ("ship", ["Docker", "Playwright"])]:
        spans = [S(k.ljust(9), CYAN), S("= [", FG)]
        for j, v in enumerate(vals):
            spans.append(S(f'"{v}"', GREEN))
            if j < len(vals) - 1: spans.append(S(", ", FG))
        spans.append(S("]", FG))
        w.add(*spans)
    return w

# ======================================================================
# 05 · git log (experience + education)
# ======================================================================
def win_log():
    w = Win("parth@github: ~")
    w.prompt('git log career --reverse --format="%ad  %s"')
    entries = [
        ("2019–2023", "init", MAG, "BE Computer Engineering · GEC Gandhinagar · CGPA 8.33", None),
        ("2023–2024", "feat", GREEN, "Software Developer @ TechBilv Solutions, India",
         "client-facing React apps · AWS IIS + S3 deploys · embedded a third-party AI chatbot"),
        ("2024-09", "feat", GREEN, "MS Computer Science @ Stevens Institute of Technology, Hoboken NJ", None),
        ("2025-09", "feat", GREEN, "Software Development Intern @ EventEase (Sep–Dec 2025)",
         "2 greenfield React 19 + TypeScript SPAs for live tournament scoring, phone → 4K TV · Redux Toolkit · shadcn/ui"),
        ("2026-05", "release", BLUE, "MS Computer Science complete · GPA 3.9", None),
    ]
    for date, kind, col, msg, detail in entries:
        w.add(S(date.ljust(11), YEL), S(kind + ": ", col, True), S(msg, WHITE))
        if detail:
            for ln in wrap_words(detail, 84):
                w.add(S(" " * 11 + "  " + ln, DIM))
    w.add(S("HEAD".ljust(11), YEL, True), S("wip: ", CYAN, True), S("your team? SWE · Full Stack · Frontend · AI/GenAI", WHITE, True))
    w.add(S(" " * 13 + "NJ/NYC metro or remote", DIM))
    return w

# ======================================================================
# 06 · contribution sparkline (static, dated)
# ======================================================================
# 52 full weeks from 2025-10-05, then the partial week Oct 4–9, 2026
WEEKS = [65,17,37,35,21,50,70,34,24,45,67,12,13,13,10,18,29,24,48,15,50,32,32,14,17,42,34,40,20,39,38,55,23,32,1,8,0,5,0,53,1,0,0,0,4,0,0,0,11,186,90,15,5]
MONTHS = [("Oct", 0), ("Nov", 4), ("Dec", 8), ("Jan", 12), ("Feb", 17), ("Mar", 21), ("Apr", 25),
          ("May", 29), ("Jun", 34), ("Jul", 38), ("Aug", 42), ("Sep", 47), ("Oct", 51)]
def win_contrib():
    w = Win("parth@github: ~")
    w.prompt("gh contrib parthkishan20 --year")
    w.add(S("1,494", GREEN, True), S(" contributions in the last year", FG), S("  ·  as of 2026-10-09", DIM))
    w.blank()
    blocks = " ▁▂▃▄▅▆▇█"
    mx = max(WEEKS)
    ROWS = 4                                   # chart height in text rows, linear scale
    top = len(w.rows)
    for _ in range(ROWS): w._row(len(w.rows))
    for i, v in enumerate(WEEKS):
        eighths = 0 if v == 0 else max(1, round(v / mx * ROWS * 8))
        col = YEL if v == mx else (G3 if v >= 40 else G2 if v >= 15 else G1)
        if v == 0:
            w.put(top + ROWS - 1, i * 2, "▁▁", "#1f2a23"); continue
        for k in range(ROWS):                  # k = 0 is the bottom row
            fill = min(8, max(0, eighths - k * 8))
            if fill: w.put(top + ROWS - 1 - k, i * 2, blocks[fill] * 2, col)
    r = w.add(S(""))
    for m, wk in MONTHS:
        w.put(r, wk * 2, m, DIM)
    w.blank()
    for k, v in [("longest streak", "239 days  (Oct 5, 2025 → May 31, 2026)"), ("active days", "263 of 370"),
                 ("peak day", "91 on Sep 13, 2026"), ("all-time", "2,783 since 2021")]:
        w.add(S(f"{k} ".ljust(17, "."), DIM), S(" " + v, WHITE))
    w.blank()
    w.prompt(caret=True)
    return w

WINDOWS = [("01-gh-fetch", win_fetch), ("02-proof", win_proof), ("03-rule-gate", win_gate),
           ("04-llm-rules", win_rules), ("05-git-log", win_log), ("06-contributions", win_contrib)]
rendered = [(name, render(fn())) for name, fn in WINDOWS]

def face(weight):
    f = TTFont(FONT_FILES[weight])
    opts = subset.Options(); opts.flavor = "woff"; opts.layout_features = []
    s = subset.Subsetter(opts); s.populate(text="".join(sorted(USED[weight])) + " ▶"); s.subset(f)
    buf = io.BytesIO(); f.flavor = "woff"; f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f'@font-face{{font-family:TermMono;font-weight:{weight};src:url(data:font/woff;base64,{b64}) format("woff")}}'

CSS = (face(400) + face(700) +
       f'.t{{font-family:TermMono,ui-monospace,monospace;font-size:{SIZE}px;fill:{FG}}}'
       '.caret{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}'
       '@media (prefers-reduced-motion:reduce){.caret{animation:none}}')

for name, (H, body) in rendered:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">'
           f'<style>{CSS}</style>{body}</svg>')
    with open(f"{OUT}/{name}.svg", "w") as fh: fh.write(svg)
    print(name, H, round(len(svg) / 1024, 1), "KB")
