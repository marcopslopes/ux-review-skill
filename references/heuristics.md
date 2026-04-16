# UX Evaluation Heuristics

## Nielsen's 10 Usability Heuristics

### H1: Visibility of System Status
The design should always keep users informed about what is going on, through appropriate feedback within a reasonable amount of time.

**What to look for:**
- Loading indicators present when content takes time
- Progress bars for multi-step processes
- Active/selected states on navigation items
- Form validation feedback (inline, not just on submit)
- Success/error confirmations after actions

### H2: Match Between System and Real World
The design should speak the users' language, with words, phrases, and concepts familiar to the user.

**What to look for:**
- Jargon-free labels (or jargon appropriate to audience)
- Icons that match real-world metaphors
- Logical information ordering (not developer-centric)
- Date/time/currency formats matching locale
- Natural reading flow (left-to-right, top-to-bottom for LTR locales)

### H3: User Control and Freedom
Users often perform actions by mistake. They need a clearly marked "emergency exit" to leave the unwanted action.

**What to look for:**
- Undo/redo support
- Cancel buttons on dialogs and forms
- Back navigation that works predictably
- Easy way to dismiss modals/overlays
- Clear way to reset filters or form fields

### H4: Consistency and Standards
Users should not have to wonder whether different words, situations, or actions mean the same thing.

**What to look for:**
- Consistent button styles for same-level actions
- Same terminology throughout (don't mix "delete" and "remove")
- Standard platform conventions followed (link colors, form patterns)
- Consistent spacing, alignment, typography hierarchy
- Icon usage consistent across pages

### H5: Error Prevention
Good design prevents problems from occurring in the first place.

**What to look for:**
- Input constraints (date pickers vs. free text for dates)
- Confirmation dialogs for destructive actions
- Disabled states for unavailable actions (with explanation)
- Smart defaults that reduce errors
- Clear formatting hints on form fields

### H6: Recognition Rather Than Recall
Minimize the user's memory load by making elements, actions, and options visible.

**What to look for:**
- Visible navigation (not hidden behind hamburger on desktop)
- Labels on icons (not icon-only buttons)
- Breadcrumbs or progress indicators
- Recently used items / search history
- Visible options rather than requiring typed commands

### H7: Flexibility and Efficiency of Use
Shortcuts for expert users speed up interaction without hindering novices.

**What to look for:**
- Keyboard shortcuts available
- Search/filter for large data sets
- Customizable views or preferences
- Autocomplete on inputs
- Power-user features that don't clutter the main interface

### H8: Aesthetic and Minimalist Design
Interfaces should not contain information that is irrelevant or rarely needed.

**What to look for:**
- Content prioritization (most important content most prominent)
- Whitespace used effectively
- No visual clutter or competing calls-to-action
- Progressive disclosure for complex information
- Every element serves a purpose

### H9: Help Users Recognize, Diagnose, and Recover from Errors
Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.

**What to look for:**
- Error messages in plain language (not error codes)
- Specific about what went wrong
- Suggest how to fix it
- Visually distinct (color, icon) but not alarming
- Positioned near the source of the error

### H10: Help and Documentation
It may be necessary to provide help and documentation. Any such information should be easy to search, focused on the task, and list concrete steps.

**What to look for:**
- Tooltips on complex form fields
- FAQ or help section accessible
- Contextual help (not just a manual dump)
- Onboarding for first-time users
- Search functionality in help content

---

## WCAG 2.1 AA — Key Checkpoints

### Perceivable

| Criterion | ID | What to Check |
|---|---|---|
| Text alternatives | 1.1.1 | All images have meaningful alt text (or empty alt for decorative) |
| Captions | 1.2.2 | Video/audio has captions or transcripts |
| Color contrast | 1.4.3 | Text contrast ratio >= 4.5:1 (normal) or >= 3:1 (large text, 18px+ bold or 24px+) |
| Resize text | 1.4.4 | Text scales to 200% without loss of content |
| Non-text contrast | 1.4.11 | UI components and graphics have >= 3:1 contrast |
| Text spacing | 1.4.12 | Content adapts to increased line height, letter/word spacing |
| Reflow | 1.4.10 | No horizontal scrolling at 320px viewport width |

### Operable

| Criterion | ID | What to Check |
|---|---|---|
| Keyboard accessible | 2.1.1 | All interactive elements reachable via keyboard |
| No keyboard trap | 2.1.2 | Focus can always move away from any element |
| Skip navigation | 2.4.1 | "Skip to main content" link present |
| Page title | 2.4.2 | Descriptive `<title>` element |
| Focus order | 2.4.3 | Tab order matches visual layout |
| Link purpose | 2.4.4 | Link text is descriptive (not "click here") |
| Focus visible | 2.4.7 | Keyboard focus indicator is visible |
| Target size | 2.5.5 | Touch targets >= 44x44 CSS pixels |

### Understandable

| Criterion | ID | What to Check |
|---|---|---|
| Language of page | 3.1.1 | `lang` attribute on `<html>` |
| On input | 3.2.2 | No unexpected context changes on input |
| Error identification | 3.3.1 | Errors clearly described in text |
| Labels | 3.3.2 | Form inputs have associated labels |
| Error suggestion | 3.3.3 | Error messages suggest corrections |
| Error prevention | 3.3.4 | Reversible/confirmed/checked submissions for legal/financial data |

### Robust

| Criterion | ID | What to Check |
|---|---|---|
| Parsing | 4.1.1 | Valid HTML (no duplicate IDs, proper nesting) |
| Name, Role, Value | 4.1.2 | Custom components have proper ARIA roles and states |
| Status messages | 4.1.3 | Status updates announced to screen readers via live regions |

---

## Scoring Guide

When scoring a category, use this rubric:

| Score | Meaning |
|---|---|
| 9-10 | Excellent — no significant issues, follows best practices |
| 7-8 | Good — minor issues only, solid foundation |
| 5-6 | Fair — several notable issues that affect experience |
| 3-4 | Poor — major issues that block or confuse users |
| 1-2 | Critical — fundamental problems, barely usable |
