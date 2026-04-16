---
name: ux-review
description: >
  Run a multi-persona UX review on any URL, local HTML file, screenshot image, or Figma frame.
  Five parallel sub-agents (configurable user, mobile low-tech user, NNG heuristic expert,
  UI quality & brand reviewer, JTBD reviewer) evaluate the page and produce a unified report
  with UX health score, cognitive walkthrough, design pattern gap analysis, priority matrix,
  and top 5 fixes. Use when the user says "ux review", "review this page", "review this site",
  "ux audit", or provides a URL/file path/Figma link and asks for UX feedback.
---

# UX Review Skill

Run a comprehensive UX evaluation using 5 parallel persona-based sub-agents.

## Prerequisites

This skill requires a Python venv with Playwright at `~/.claude/skills/ux-review/venv/`.

**First-run check:** Before doing anything else, verify the venv exists:

```bash
test -f ~/.claude/skills/ux-review/venv/bin/python && ~/.claude/skills/ux-review/venv/bin/python -c "import playwright" 2>/dev/null
```

If that fails, tell the user:

> Playwright is not set up yet. Run these commands to install (one-time, ~500MB for Chromium):
>
> ```
> python3 -m venv ~/.claude/skills/ux-review/venv
> source ~/.claude/skills/ux-review/venv/bin/activate
> pip install playwright
> playwright install chromium
> ```
>
> Then re-run `/ux-review`.

**Do NOT proceed until the venv check passes.** Exception: Mode 3 (screenshot) and Mode 4 (Figma) do not require Playwright — skip the check for those modes.

---

## Step 1 — Detect Input Mode

Auto-detect the input mode from the argument. No extra questions — just pattern match:

| Mode | Detection rule | Example inputs |
|---|---|---|
| **Mode 1: Live URL** | Starts with `http://` or `https://` (not figma.com) | `https://booksy.com` |
| **Mode 2: Local HTML** | File path ending in `.html` or `.htm` | `./prototype.html`, `/path/to/index.html` |
| **Mode 3: Screenshot** | File path ending in `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | `./design.png`, `~/screens/home.jpg` |
| **Mode 4: Figma** | Contains `figma.com` in URL, or user mentions "figma" | `https://figma.com/design/...`, "review my Figma frame" |

Extract the **site name** for the report filename:
- `https://www.example.com/pricing` → `example-com`
- `./prototype.html` → `prototype`
- `./design.png` → `design`
- Figma URL → extract file name or use `figma-review`

Set a `mode` variable (1, 2, 3, or 4) used throughout the remaining steps.

---

## Step 2 — Prepare Artifacts (mode-dependent)

### Mode 1: Live URL

No preparation needed. URL is used directly in Step 4.

### Mode 2: Local HTML File

1. Verify the file exists
2. Pick a random port between 8000-9000
3. Start a background HTTP server:
   ```bash
   python3 -m http.server PORT --directory "PARENT_DIR" &
   ```
4. Record the PID for cleanup in Step 8
5. Construct the URL: `http://localhost:PORT/FILENAME`
6. **Additionally**, read the raw HTML source directly with the Read tool and extract:
   - All `<form>` elements with their fields, validation attributes (`required`, `pattern`, `type`, `minlength`, `maxlength`)
   - All interactive elements (`<button>`, `<a>`, `<input>`, `<select>`, elements with `onclick`/`@click`)
   - CSS `@media` queries (responsive breakpoints)
   - Whether JavaScript event handlers are present (click, submit, change listeners)
7. Save this as `code-analysis.md` in the output directory — passed to all agents as extra context

### Mode 3: Screenshot Image

1. Verify the image file exists
2. Copy (or note the path to) the image file — this becomes the sole artifact
3. Create the output directory at `/tmp/ux-review-TIMESTAMP/`
4. Copy the image as `screenshot.png` into the output directory
5. **No Playwright, no DOM, no a11y tree.** Set flags:
   - `has_dom = false`
   - `has_a11y = false`

### Mode 4: Figma

1. Invoke the `figma:figma-use` skill to load Figma tool prerequisites
2. If the user provided a Figma URL, parse the `fileKey` and `nodeId` from it
3. If no specific frame/node was mentioned, ask ONE question using AskUserQuestion:
   > "Which frame or screen should I review?"
4. Use `get_screenshot` (from Figma MCP) to export the specified frame as a PNG
5. Save the exported image as `screenshot.png` in the output directory
6. **No DOM, no a11y tree.** Set flags:
   - `has_dom = false`
   - `has_a11y = false`
   - `is_figma = true`

---

## Step 3 — Ask Persona A Configuration (2 questions max)

Ask the user exactly two questions using AskUserQuestion, one at a time:

**Question 1:**
> Who is Persona A for this review? (e.g. "senior developer", "first-time shopper", "enterprise IT admin")

**Question 2:**
> What device are they on? (e.g. "desktop", "iPad", "iPhone 14")

Map the device answer to a Playwright device descriptor (used in Mode 1 and 2 only):
- "desktop" → `"Desktop Chrome"`
- "iphone" / "iphone 14" → `"iPhone 14"`
- "iphone 15" → `"iPhone 15"`
- "ipad" → `"iPad Pro 11"`
- "android" / "pixel" → `"Pixel 7"`
- Other → `"Desktop Chrome"` (default, note in report)

---

## Step 4 — Capture Page Artifacts (Mode 1 and 2 only)

**Skip this step for Mode 3 and Mode 4** — artifacts are already prepared in Step 2.

Run the Playwright capture script ONCE:

```bash
~/.claude/skills/ux-review/venv/bin/python ~/.claude/skills/ux-review/scripts/run_persona.py \
  --url "TARGET_URL" \
  --output-dir "/tmp/ux-review-TIMESTAMP" \
  --device "DEVICE_DESCRIPTOR" \
  --timeout 30000
```

This produces:
- `screenshot.png` — full-page screenshot
- `dom.html` — cleaned DOM (scripts stripped)
- `a11y-tree.txt` — accessibility tree snapshot
- `metadata.json` — capture metadata
- `error.txt` — only if capture failed

**If `error.txt` exists:** Read it, report the error to the user, kill the HTTP server if running, and stop.

---

## Step 4b — Read Artifacts Into Memory (CRITICAL)

**Sub-agents cannot read files from `/tmp/` due to permission restrictions.** The parent agent MUST read all artifacts into memory here, then embed the content directly in each sub-agent prompt in Step 5.

### For Mode 1 and Mode 2:

1. **Screenshot** — Read the screenshot image file using the Read tool. Write a detailed visual description (300-500 words) covering:
   - Header layout and elements
   - Hero section content, colors, typography
   - Any overlays or dialogs visible
   - Below-fold sections in scroll order
   - Footer content
   - Overall visual impression
   Store this as `screenshot_description` for embedding in agent prompts.

2. **Accessibility tree** — Read the full `a11y-tree.txt` file using the Read tool. Store the complete text content as `a11y_tree_content` for embedding verbatim in agent prompts. This file is typically 100-300 lines and fits easily in a prompt.

3. **DOM** — The `dom.html` file is often very large (30K+ tokens). Do NOT attempt to embed it in full. Instead:
   - Read it using the Read tool (use offset/limit if it exceeds the Read tool's token limit)
   - Extract and summarize the key structural findings as `dom_summary` (200-400 words):
     - What elements are used for interactive components (buttons vs spans vs divs)
     - Form fields and their attributes (labels, required, validation patterns)
     - Heading hierarchy (H1, H2, H3 structure)
     - Any accessibility issues visible in the HTML (missing alt, missing labels, non-semantic elements)
     - Notable CSS or layout patterns
     - Any hidden content (display:none, aria-hidden)
   - Include specific code snippets for problematic elements (e.g., a city list using `<span>` instead of `<button>`)

4. **Code analysis (Mode 2 only)** — Read the `code-analysis.md` file and store as `code_analysis_content`.

### For Mode 3 and Mode 4:

1. **Screenshot only** — Read the screenshot image file using the Read tool. Write a detailed visual description (300-500 words) as `screenshot_description`. This is the sole artifact.

---

## Step 5 — Dispatch 5 Sub-Agents in Parallel

Read the reference files to construct agent prompts:
- Read `~/.claude/skills/ux-review/references/persona-generic.md` for prompt templates
- Read `~/.claude/skills/ux-review/references/heuristics.md` for Persona C's evaluation framework
- Read `~/.claude/skills/ux-review/references/trends.md` for current UX best practices context

Launch exactly 5 agents **in parallel** using the Agent tool.

### Artifact Embedding Per Mode

**IMPORTANT: Sub-agents cannot access files in `/tmp/`. All artifact content MUST be embedded directly in the agent prompt text. Never pass file paths to sub-agents.**

**Mode 1 (Live URL) and Mode 2 (Local HTML):**
Each agent prompt includes these sections with the content from Step 4b:
- `SCREENSHOT DESCRIPTION:` followed by `screenshot_description`
- `ACCESSIBILITY TREE (full):` followed by `a11y_tree_content` (verbatim)
- `KEY DOM FINDINGS:` followed by `dom_summary`
- Mode 2 agents also receive `CODE ANALYSIS:` followed by `code_analysis_content`

**Mode 3 (Screenshot) and Mode 4 (Figma):**
Each agent prompt includes `SCREENSHOT DESCRIPTION:` followed by `screenshot_description`. Add this context:

```
NOTE: This is a visual-only review ({source}). No DOM or accessibility tree is available.
- Evaluate based on what you can see in the screenshot description only
- Skip any checks that require DOM inspection or accessibility tree data
- For WCAG checks, only evaluate what is visually assessable (contrast, text size, tap targets, visual hierarchy)
- Do NOT score the Accessibility (WCAG) category — leave it out of your scores
```

Where `{source}` is "screenshot image" for Mode 3 or "Figma design export" for Mode 4.

### Agent Prompts

Each agent receives:
1. Its persona prompt (from persona-generic.md, with variables filled in)
2. The artifact content embedded directly in the prompt (from Step 4b — NEVER file paths)
3. The trends.md content as additional context
4. Agent C also receives the full heuristics.md content
5. Explicit instruction to return **valid JSON only** in the format specified in its prompt template

### Agent A — Configurable Persona

```
prompt: |
  You are conducting a UX review as a specific user persona.

  YOUR PERSONA:
  - Tech level: {user's answer to Q1}
  - Device: {user's answer to Q2}

  {Insert Agent A prompt template from persona-generic.md}

  PAGE BEING REVIEWED: {URL or file path}

  SCREENSHOT DESCRIPTION:
  {Insert screenshot_description from Step 4b}

  ACCESSIBILITY TREE (full):
  {Insert a11y_tree_content from Step 4b — verbatim, or omit for Mode 3/4}

  KEY DOM FINDINGS:
  {Insert dom_summary from Step 4b — or omit for Mode 3/4}

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

### Agent B — Mobile Low-Tech Persona

```
prompt: |
  You are conducting a UX review as a low-tech mobile user.

  {Insert Agent B prompt template from persona-generic.md}

  PAGE BEING REVIEWED: {URL or file path}

  SCREENSHOT DESCRIPTION:
  {Insert screenshot_description from Step 4b}

  ACCESSIBILITY TREE (full):
  {Insert a11y_tree_content from Step 4b — verbatim, or omit for Mode 3/4}

  KEY DOM FINDINGS:
  {Insert dom_summary from Step 4b — or omit for Mode 3/4}

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

### Agent C — NNG Heuristic Expert

```
prompt: |
  You are a senior UX researcher conducting a formal heuristic evaluation.

  {Insert Agent C prompt template from persona-generic.md}

  HEURISTIC FRAMEWORK:
  {Insert full heuristics.md content}

  PAGE BEING REVIEWED: {URL or file path}

  SCREENSHOT DESCRIPTION:
  {Insert screenshot_description from Step 4b}

  ACCESSIBILITY TREE (full):
  {Insert a11y_tree_content from Step 4b — verbatim, or omit for Mode 3/4}

  KEY DOM FINDINGS:
  {Insert dom_summary from Step 4b — or omit for Mode 3/4}

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

### Agent D — UI Quality & Brand Reviewer

```
prompt: |
  You are a senior visual designer evaluating UI quality and brand coherence.

  {Insert Agent D prompt template from persona-generic.md}

  PAGE BEING REVIEWED: {URL or file path}

  SCREENSHOT DESCRIPTION:
  {Insert screenshot_description from Step 4b}

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

Note: Agent D receives only the screenshot description — DOM/a11y details are not relevant for visual design evaluation.

### Agent E — Jobs To Be Done Reviewer

```
prompt: |
  You are a product strategist applying the JTBD framework to evaluate this page.

  {Insert Agent E prompt template from persona-generic.md}

  PAGE BEING REVIEWED: {URL or file path}

  SCREENSHOT DESCRIPTION:
  {Insert screenshot_description from Step 4b}

  ACCESSIBILITY TREE HIGHLIGHTS:
  {Insert key highlights from a11y_tree_content — interactive elements, CTAs, navigation structure, or omit for Mode 3/4}

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

Note: Agent E receives a11y highlights (not full tree) focused on interactive elements and CTAs relevant to job completion.

---

## Step 6 — Compile Unified Report

Once all 5 agents return, parse their JSON responses and compile:

### 6a. Calculate Scores

For each category, average only the scores that were provided:

**Mode 1 and 2 (full artifacts):**

| Category | Scored by | Average across |
|---|---|---|
| Usability | A, B, C | 3 agents |
| Accessibility (WCAG) | C only | 1 agent |
| Visual Clarity | A, B, C | 3 agents |
| Navigation & Flow | A, C | 2 agents |
| Error Prevention | B, C | 2 agents |
| UI Quality | D only | 1 agent |
| Jobs To Be Done | E only | 1 agent |

**Mode 3 and 4 (visual only — no Accessibility score):**

| Category | Scored by | Average across |
|---|---|---|
| Usability | A, B, C | 3 agents |
| Visual Clarity | A, B, C | 3 agents |
| Navigation & Flow | A, C | 2 agents |
| Error Prevention | B, C | 2 agents |
| UI Quality | D only | 1 agent |
| Jobs To Be Done | E only | 1 agent |

**Overall Score** = (average of all scored category scores) x (100/10), rounded to nearest integer. Out of 100.

### 6b. Deduplicate, Rank & Assign Effort

1. Collect all issues from all 5 agents
2. Group similar issues (same element/area + same problem)
3. For grouped issues, keep the most specific recommendation and note **which agents flagged it**
4. **Cross-agent agreement rule:** Any issue flagged by 3+ agents is automatically elevated to Critical severity
5. Assign **effort estimate** to every issue:
   - **Low** — CSS/copy change, config tweak, single-file edit (< 1 hour)
   - **Medium** — Component refactor, new element, moderate code change (1-4 hours)
   - **High** — Architecture change, new feature, multi-file refactor (4+ hours)
6. Sort by: critical > major > minor, then by number of agents who flagged it
7. Select **Top 5 Priority Fixes** from the sorted list

### 6c. Enrich Each Issue

Before writing the report, enrich every issue (top 5 and per-agent) with these fields. Infer them from the agent's finding, the screenshot, and the DOM (if available):

- **Location** — Where on the page (e.g. "Hero section search bar", "Footer social links", "Cookie dialog")
- **Why** — One sentence: what goes wrong for the user (combines the old Flow + Moment fields)
- **Fix** — One sentence: specific, actionable recommendation
- **Effort** — Low / Medium / High (from step 6b)
- **Agents** — Which agents flagged this issue (e.g. "A, B, C")

### 6d. Build Cognitive Walkthrough

Construct a step-by-step walkthrough of the **primary user flow** on the page (inferred from the page's purpose — e.g. "Book an appointment", "Sign up", "Find a product"). Use the screenshot, DOM, and all agent findings to populate it.

Steps should follow the user's natural journey from landing to completing their goal. For each step, assess the risk level based on the issues found at that point.

### 6e. Build Design Pattern Gaps

Check the page for the presence of 10 standard UX patterns. Determine status from the DOM, a11y tree, and screenshot. For Mode 3/4 (visual only), assess only what's visible in the screenshot.

**Only evaluate patterns relevant to the page type being reviewed.** A homepage does not need a progress indicator or save-draft — mark those N/A. A multi-step form does. Judge each pattern against what the page actually is, not against an abstract checklist.

Patterns to check:
1. Progress indicator (for multi-step flows)
2. Save draft / auto-save
3. Required field legend / indicator
4. Help/support link
5. Breadcrumb navigation
6. Mobile responsiveness
7. Error recovery (undo, back, cancel)
8. Confirmation step before submit
9. Empty states
10. Loading states

### 6f. Build Priority Matrix

Create a matrix of ALL deduplicated issues ranked by Severity + Effort:

| Priority | Rule |
|---|---|
| **P1** | Critical severity, any effort — OR — any severity flagged by 3+ agents |
| **P2** | Major severity + Low/Medium effort — OR — Minor severity flagged by 2+ agents |
| **P3** | Everything else |

### 6g. Write the Report

Save to: `{cwd}/ux-review-{site-name}-{date}.md`

**Format guardrails:**
- Markdown only, no raw HTML
- Max 500 lines total
- Per-agent narrative: max 150 words
- No nested lists deeper than 2 levels
- Report should feel like a clean Notion doc, not a dashboard
- Reserve emojis for health score indicators and severity labels ONLY — no emoji on every line
- Clean whitespace between sections (use `---` dividers)

**Score emoji indicators (used in health score table only):**
- 🔴 below 5
- 🟡 5-7
- 🟢 above 7

**Effort labels (plain text, no emoji):**
- Low
- Medium
- High

Use this structure:

```markdown
# UX Review: {site-name}

**Date:** {YYYY-MM-DD}
**URL:** {target URL or file path}
**Mode:** {Live URL | Local HTML | Screenshot | Figma}
**Personas:** A: {tech level} on {device} · B: Mobile low-tech · C: NNG heuristics · D: UI quality · E: JTBD

{If Mode 3 or 4, add this notice:}
> Visual-only review — no DOM or accessibility data available. Export to HTML and rerun for full WCAG audit.

---

## UX Health Score: {overall}/100

| Category | Score | |
|---|---|---|
| Usability | {score}/10 | {emoji} |
| Accessibility (WCAG) | {score}/10 | {emoji} |
| Visual Clarity | {score}/10 | {emoji} |
| Navigation & Flow | {score}/10 | {emoji} |
| Error Prevention | {score}/10 | {emoji} |
| UI Quality | {score}/10 | {emoji} |
| Jobs To Be Done | {score}/10 | {emoji} |

{For Mode 3/4, omit the Accessibility row and add: *Accessibility score requires DOM — not available in visual-only mode.*}

---

## Top 5 Priority Fixes

**1. {Title}**
**Why:** {One sentence — what goes wrong for the user}
**Fix:** {One sentence — specific, actionable recommendation}
**Effort:** {Low / Medium / High} · **Flagged by:** {A, B, C, D, E}

**2. {Title}**
**Why:** {one sentence}
**Fix:** {one sentence}
**Effort:** {effort} · **Flagged by:** {agents}

**3. {Title}**
**Why:** ...
**Fix:** ...
**Effort:** ... · **Flagged by:** ...

**4. {Title}**
**Why:** ...
**Fix:** ...
**Effort:** ... · **Flagged by:** ...

**5. {Title}**
**Why:** ...
**Fix:** ...
**Effort:** ... · **Flagged by:** ...

---

## Cognitive Walkthrough: {primary flow name}

| Step | Action | Risk | Issue |
|---|---|---|---|
| 1 | {User lands on page} | {🟢 Low / 🟡 Medium / 🟠 High / 🔴 Critical} | {Primary issue at this step, or "None"} |
| 2 | {User looks for search/CTA} | ... | ... |
| 3 | ... | ... | ... |

---

## Design Pattern Gaps

| Pattern | Status |
|---|---|
| Progress indicator | {✅ Present / ❌ Missing / ⚠️ Broken / N/A} |
| Save draft / auto-save | ... |
| Required field legend | ... |
| Help/support link | ... |
| Breadcrumb navigation | ... |
| Mobile responsiveness | ... |
| Error recovery | ... |
| Confirmation before submit | ... |
| Empty states | ... |
| Loading states | ... |

---

## Detailed Findings

### Agent A — {tech level} on {device}

{Agent A's narrative — max 150 words, plain paragraph, no sub-headers}

| # | Finding | Location | Effort | Agents |
|---|---|---|---|---|
| 1 | {finding} | {location} | {Low/Med/High} | {A, B, ...} |
| 2 | ... | ... | ... | ... |

### Agent B — Mobile Low-Tech User

{narrative — max 150 words}

| # | Finding | Location | Effort | Agents |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

### Agent C — NNG Heuristic Expert

{narrative — max 150 words}

| # | Finding | Location | Effort | Agents |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

### Agent D — UI Quality & Brand

{narrative — max 150 words}

| # | Finding | Location | Effort | Agents |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

### Agent E — Jobs To Be Done

{narrative — max 150 words}

| # | Finding | Location | Effort | Agents |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |

---

## Priority Matrix

| Issue | Effort | Agents | Priority |
|---|---|---|---|
| {issue title} | {Low/Med/High} | A, B, C | **P1** |
| {issue title} | {Low/Med/High} | B, C | **P2** |
| {issue title} | {Low/Med/High} | C | **P3** |
| ... | ... | ... | ... |
```

**Table rules:**
- Issues tables (per-agent): 5 columns max — #, Finding, Location, Effort, Agents
- Rows ordered by priority (most critical first) — row order encodes severity, no Sev column needed
- Priority matrix: 4 columns — Issue, Effort, Agents, Priority
- No emoji in tables except the health score table

### 6h. Print Terminal Summary

After writing the file, print a concise summary to the terminal. **Max 15 lines.** Clean, no emoji clutter.

```
UX Review: {site-name} — {overall}/100

  Usability          {score}/10  {emoji}
  Accessibility      {score}/10  {emoji}
  Visual Clarity     {score}/10  {emoji}
  Navigation & Flow  {score}/10  {emoji}
  Error Prevention   {score}/10  {emoji}
  UI Quality         {score}/10  {emoji}
  Jobs To Be Done    {score}/10  {emoji}

Top fixes:
  1. {title} ({effort})
  2. {title} ({effort})
  3. {title} ({effort})
  4. {title} ({effort})
  5. {title} ({effort})

Saved: {filename}
```

---

## Step 7 — Cleanup

1. If an HTTP server was started in Step 2, kill it: `kill PID`
2. Optionally clean up `/tmp/ux-review-TIMESTAMP/` artifacts (or leave for debugging)

---

## Error Handling

- **Playwright not installed:** Detected in prerequisite check. Print setup instructions and stop. (Skipped for Mode 3/4.)
- **Page load failure:** `error.txt` created by script. Report to user, skip review, cleanup.
- **File not found (Mode 2/3):** Report to user that the file path doesn't exist. Stop.
- **Figma access failure (Mode 4):** Report Figma MCP error to user. Suggest checking authentication. Stop.
- **One agent fails:** Compile report from the agents that succeeded. Note the missing persona in the report header. Adjust score averages to only include available scores.
- **All agents fail:** Report the error to the user. Cleanup.
- **HTTP server cleanup:** Always kill the server process, even if agents fail. Use the recorded PID.
- **JSON parse failure from agent:** If an agent returns invalid JSON, attempt to extract JSON from the response using regex (`\{[\s\S]*\}`). If that fails, skip that agent and note it in the report.
