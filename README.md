# UX Review Skill

Multi-persona UX review for any web page, prototype, screenshot, or Figma frame.

## Quick Start

```
/ux-review https://example.com
/ux-review ./prototype.html
/ux-review ./design.png
/ux-review https://figma.com/design/ABC123/...
```

## Setup (one-time)

```bash
python3 -m venv ~/.claude/skills/ux-review/venv
source ~/.claude/skills/ux-review/venv/bin/activate
pip install playwright
playwright install chromium
```

Playwright is only required for Mode 1 (Live URL) and Mode 2 (Local HTML). Screenshot and Figma modes work without it.

## Input Modes

| Mode | Input | Artifacts | Accessibility Score |
|---|---|---|---|
| **1. Live URL** | `https://...` | Screenshot + DOM + A11y tree | Yes |
| **2. Local HTML** | `./file.html` | Screenshot + DOM + A11y tree + code analysis | Yes |
| **3. Screenshot** | `./file.png` or `.jpg` | Screenshot only | No (visual only) |
| **4. Figma** | Figma URL or "review my Figma" | Exported screenshot only | No (visual only) |

**Mode 2** additionally extracts form fields, validation rules, interactive elements, CSS media queries, and JS event handlers from the raw HTML source for deeper code-level analysis.

**Mode 3 and 4** produce visual-only reviews. The report notes this limitation and suggests exporting to HTML for a full audit.

## Agents

All 5 agents run in parallel on the same artifacts:

| Agent | Role | Scores |
|---|---|---|
| **A** | Configurable persona (you choose tech level + device) | Usability, Visual Clarity, Navigation & Flow |
| **B** | Mobile low-tech user (62yo, smartphone, limited tech) | Usability, Visual Clarity, Error Prevention |
| **C** | NNG heuristic expert (Nielsen 10 + WCAG 2.1 AA) | All 7 categories |
| **D** | UI Quality & Brand reviewer | UI Quality |
| **E** | Jobs To Be Done reviewer | Jobs To Be Done |

## Report Output

Report saved as `ux-review-{site-name}-{date}.md` in your current working directory.

### Sections

1. **UX Health Score** — Overall /100 + 7 category scores with emoji bars
2. **Top 5 Priority Fixes** — Each with location, flow, moment, fix, and effort estimate
3. **Cognitive Walkthrough** — Step-by-step user journey with risk level per step
4. **Design Pattern Gaps** — 10 standard patterns checked (present/missing/broken)
5. **Detailed Findings** — Per-agent narrative (200 words max) + issues table
6. **Priority Matrix** — All issues ranked P1/P2/P3 by severity + effort

### Scoring

- 7 categories, each /10, averaged to /100 overall
- Emoji indicators: 🔴 below 5 | 🟡 5-7 | 🟢 above 7
- Severity: 🔴 Critical | 🟠 Major | 🟡 Minor
- Effort: ⚡ Low | 🔧 Medium | 🏗️ High
- Priority: P1 (do now) | P2 (do soon) | P3 (backlog)

### Cross-Agent Agreement

Issues flagged by 3+ agents are automatically elevated to Critical. The "Agents" column in every table shows which agents flagged each issue.

### Issue Format

Every issue includes:
- 📍 **Location** — where on the page
- 🔄 **Flow** — which user journey it interrupts
- 💥 **Moment** — what the user experiences
- ✅ **Fix** — specific recommendation

## File Structure

```
~/.claude/skills/ux-review/
├── SKILL.md                      # Orchestration logic
├── README.md                     # This file
├── scripts/
│   └── run_persona.py            # Playwright capture (screenshot + DOM + a11y tree)
├── references/
│   ├── heuristics.md             # Nielsen 10 + WCAG 2.1 AA checklist
│   ├── persona-generic.md        # Prompt templates for all 5 agents
│   └── trends.md                 # UX best practices 2024-2026
└── venv/                         # Python venv (created on setup, not committed)
```
