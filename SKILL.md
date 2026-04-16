---
name: ux-review
description: >
  Run a multi-persona UX review on any URL or local HTML file. Three parallel sub-agents
  (configurable user, mobile low-tech user, NNG heuristic expert) evaluate the page and
  produce a unified report with a UX health score and top 5 priority fixes. Use when the
  user says "ux review", "review this page", "review this site", "ux audit", or provides
  a URL/file path and asks for UX feedback.
---

# UX Review Skill

Run a comprehensive UX evaluation using 3 parallel persona-based sub-agents.

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

**Do NOT proceed until the venv check passes.** Stop here and wait for the user.

---

## Step 1 — Parse Input

The user provides a target as the skill argument. Determine if it's:

- **A URL** (starts with `http://` or `https://`) — use directly
- **A local file path** — needs an HTTP server (Step 2)

Extract the **site name** from the URL for the report filename:
- `https://www.example.com/pricing` → `example-com`
- `/path/to/index.html` → `index-html`

---

## Step 2 — Start HTTP Server (local files only)

If the input is a local file path:

1. Pick a random port between 8000-9000
2. Start a background HTTP server:
   ```bash
   python3 -m http.server PORT --directory "PARENT_DIR" &
   ```
3. Record the PID so you can kill it in Step 7
4. Construct the URL: `http://localhost:PORT/FILENAME`

If the input is already a URL, skip this step.

---

## Step 3 — Ask Persona A Configuration (2 questions max)

Ask the user exactly two questions using AskUserQuestion, one at a time:

**Question 1:**
> Who is Persona A for this review? (e.g. "senior developer", "first-time shopper", "enterprise IT admin")

**Question 2:**
> What device are they on? (e.g. "desktop", "iPad", "iPhone 14")

Map the device answer to a Playwright device descriptor:
- "desktop" → `"Desktop Chrome"`
- "iphone" / "iphone 14" → `"iPhone 14"`
- "iphone 15" → `"iPhone 15"`
- "ipad" → `"iPad Pro 11"`
- "android" / "pixel" → `"Pixel 7"`
- Other → `"Desktop Chrome"` (default, note in report)

---

## Step 4 — Capture Page Artifacts

Run the Playwright capture script ONCE to collect artifacts for all agents:

```bash
~/.claude/skills/ux-review/venv/bin/python ~/.claude/skills/ux-review/scripts/run_persona.py \
  --url "TARGET_URL" \
  --output-dir "/tmp/ux-review-TIMESTAMP" \
  --device "DEVICE_DESCRIPTOR" \
  --timeout 30000
```

This produces in the output directory:
- `screenshot.png` — full-page screenshot
- `dom.html` — cleaned DOM (scripts stripped)
- `a11y-tree.txt` — accessibility tree snapshot
- `metadata.json` — capture metadata
- `error.txt` — only if capture failed

**If `error.txt` exists:** Read it, report the error to the user, kill the HTTP server if running, and stop.

---

## Step 5 — Dispatch 3 Sub-Agents in Parallel

Read the reference files to construct agent prompts:
- Read `~/.claude/skills/ux-review/references/persona-generic.md` for prompt templates
- Read `~/.claude/skills/ux-review/references/heuristics.md` for Persona C's evaluation framework
- Read `~/.claude/skills/ux-review/references/trends.md` for current UX best practices context

Launch exactly 3 agents **in parallel** using the Agent tool. Each agent receives:
1. Its persona prompt (from persona-generic.md, with variables filled in)
2. The paths to all 3 artifact files to read
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

  ARTIFACTS TO REVIEW:
  - Screenshot: Read the file at {output_dir}/screenshot.png
  - DOM: Read the file at {output_dir}/dom.html
  - Accessibility tree: Read the file at {output_dir}/a11y-tree.txt

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

### Agent B — Mobile Low-Tech Persona

```
prompt: |
  You are conducting a UX review as a low-tech mobile user.

  {Insert Agent B prompt template from persona-generic.md}

  ARTIFACTS TO REVIEW:
  - Screenshot: Read the file at {output_dir}/screenshot.png
  - DOM: Read the file at {output_dir}/dom.html
  - Accessibility tree: Read the file at {output_dir}/a11y-tree.txt

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

  ARTIFACTS TO REVIEW:
  - Screenshot: Read the file at {output_dir}/screenshot.png
  - DOM: Read the file at {output_dir}/dom.html
  - Accessibility tree: Read the file at {output_dir}/a11y-tree.txt

  CURRENT UX TRENDS (use as context):
  {Insert trends.md content}

  IMPORTANT: Return ONLY valid JSON in the format specified above. No markdown, no explanation outside the JSON.
```

---

## Step 6 — Compile Unified Report

Once all 3 agents return, parse their JSON responses and compile:

### 6a. Calculate Scores

For each of the 5 categories, average only the scores that were provided:

| Category | Scored by | Average across |
|---|---|---|
| Usability | A, B, C | 3 agents |
| Accessibility (WCAG) | C only | 1 agent |
| Visual Clarity | A, B, C | 3 agents |
| Navigation & Flow | A, C | 2 agents |
| Error Prevention | B, C | 2 agents |

**Overall Score** = (average of all 5 category scores) × 10, rounded to nearest integer. Out of 100.

### 6b. Deduplicate & Rank Issues

1. Collect all issues from all 3 agents
2. Group similar issues (same element/area + same problem)
3. For grouped issues, keep the most specific recommendation and note which personas flagged it
4. Sort by: critical > major > minor, then by number of personas who flagged it
5. Select **Top 5 Priority Fixes** from the sorted list

### 6c. Write the Report

Save to: `{cwd}/ux-review-{site-name}-{date}.md`

Use this structure:

```markdown
# UX Review: {site-name}

**Date:** {YYYY-MM-DD}
**URL:** {target URL}
**Personas:**
- A: {tech level} on {device}
- B: Mobile low-tech user (62yo, smartphone, limited tech experience)
- C: NNG heuristic expert (Nielsen 10 + WCAG 2.1 AA)

---

## UX Health Score: {overall}/100

| Category | Score |
|---|---|
| Usability | {x}/10 |
| Accessibility (WCAG) | {x}/10 |
| Visual Clarity | {x}/10 |
| Navigation & Flow | {x}/10 |
| Error Prevention | {x}/10 |

---

## Top 5 Priority Fixes

### 1. {Title}
**Severity:** {critical/major/minor} | **Category:** {category} | **Flagged by:** {personas}

{Finding description}

**Recommendation:** {How to fix it}

### 2. {Title}
...

### 3. {Title}
...

### 4. {Title}
...

### 5. {Title}
...

---

## Detailed Findings

### Persona A: {tech level} on {device}

{Agent A's narrative}

**Issues found:** {count}
{List each issue with severity, category, finding, recommendation}

### Persona B: Mobile Low-Tech User

{Agent B's narrative}

**Issues found:** {count}
{List each issue with severity, category, finding, recommendation}

### Persona C: NNG Heuristic Expert

{Agent C's narrative}

**Issues found:** {count}
{List each issue with severity, category, finding, recommendation}
```

### 6d. Print Terminal Summary

After writing the file, print a concise summary to the terminal:

```
UX Review Complete: {site-name}
Score: {overall}/100

  Usability:        {x}/10
  Accessibility:    {x}/10
  Visual Clarity:   {x}/10
  Navigation & Flow:{x}/10
  Error Prevention: {x}/10

Top 5 Fixes:
  1. {title} ({severity})
  2. {title} ({severity})
  3. {title} ({severity})
  4. {title} ({severity})
  5. {title} ({severity})

Full report saved to: {filename}
```

---

## Step 7 — Cleanup

1. If an HTTP server was started in Step 2, kill it: `kill PID`
2. Optionally clean up `/tmp/ux-review-TIMESTAMP/` artifacts (or leave for debugging)

---

## Error Handling

- **Playwright not installed:** Detected in prerequisite check. Print setup instructions and stop.
- **Page load failure:** `error.txt` created by script. Report to user, skip review, cleanup.
- **One agent fails:** Compile report from the 2 that succeeded. Note the missing persona in the report header. Adjust score averages to only include available scores.
- **All agents fail:** Report the error to the user. Cleanup.
- **HTTP server cleanup:** Always kill the server process, even if agents fail. Use the recorded PID.
- **JSON parse failure from agent:** If an agent returns invalid JSON, attempt to extract JSON from the response using regex (`\{[\s\S]*\}`). If that fails, skip that agent and note it in the report.
