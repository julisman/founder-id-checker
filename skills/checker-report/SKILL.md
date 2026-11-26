---
name: checker-report
description: >-
  The business check-up report for an Indonesian business that is already open.
  Compiles everything the other checker skills wrote (the real numbers, the
  channels, what customers say, the competitors now, the papers and the board's
  vote) into one report with a verdict at the top that is computed from the
  numbers, never written by hand: Sehat (healthy), Waspada (watch out), Kritis
  (critical) or Incomplete. Adds the top three fixes ranked by Rupiah a month, a
  90-day plan with a number to check each month, and a one-page version for a
  partner, an investor or a bank (for a KUR loan, for example). Use when the
  owner says "give me the report", "hasil cek bisnis", "put it all together",
  "what should I do first", "rencana 90 hari", or at the end of the checker.
argument-hint: "[--for bank | partner | investor]"
---

# checker-report

The last step. One report the owner can act on, built only from what the
checker found.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir checker
```

## Step 1: see what is there

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir checker --check
```

prints the verdict and each check, computed by the health tool from
`checker/actuals.json`, `checker/customers.json` and `checker/compliance.json`.
No actuals: the verdict is Incomplete; run `/checker-intake`. List the missing
sections with the skill that fills each. Do not fill a missing section from
guesses.

## Step 2: the summary

Write `checker/summary.md`, half a page, plain words:

- What the business is, where, and since when, in one sentence.
- The verdict and the three numbers behind it (net profit a month, how far above
  or below break-even, what it keeps after the owner and the debt).
- What customers and competitors show, in two sentences.
- The board's vote, and where members disagreed.
- The one thing to do this week.

If the verdict is Kritis, lead with what has to change and which skill changes
it. Never soften a failing check.

## Step 3: the 90-day plan

Write `checker/plan-90.md`. Start from the top fixes the tool ranked (they are
in the report under "The top 3 fixes") and the board's conditions. Three months,
three to five actions each, every action with:

- who does it (the owner, a named role),
- the number it moves and the target (direct cost from 38.5% to 35%, rating from
  3.2 to 4.0, app orders moved to WhatsApp from 0 to 50 a week),
- the date to check it.

Respect the calendar: no big change in the two weeks before Lebaran, cash ready
for THR, the rainy season for delivery. Check
`${CLAUDE_SKILL_DIR}/../checker-compliance/reference/calendar.md`. The first
month fixes what is critical; growth comes after the numbers say Sehat.

End with the re-check: run `/checker-intake` with the new months and
`/checker-report` again in 90 days, and compare the verdicts.

## Step 4: compile

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir checker
```

writes `checker/report.md`: the title, the verdict and its checks, the key
numbers, the top 3 fixes, the business, then every section the checker produced
(summary, 90-day plan, board, numbers, channels, customers, competitors,
compliance), and what is not done yet. The numbers section is rebuilt from
`checker/actuals.json` each time, so it always matches the verdict.

## Step 5: the one-pager

Write `checker/one-pager.md` for someone deciding in two minutes: what the
business is and how long it has run, the key numbers table (word for word from
the report), the verdict, the evidence (months of records, rating, survey), the
plan, and, if there is one, the ask. For a bank (`--for bank`): add the legal
form, the NIB, twelve months of turnover if the records have them, the existing
debt and its payment, and what the loan is for; do not promise a loan
programme's terms without linking them. For a partner or investor: what the
money would change, in the numbers.

## Rules

- The verdict comes from the tool. Never write Sehat by hand, and never round a
  failing number into a passing one.
- Say once: every number is the owner's own record, estimates are marked, the
  reviews and answers are from real customers. Not financial, legal or tax advice.
- If the owner wants a PDF, a Word file or a deck, offer to export it, but keep
  the markdown as the source of truth.

## Output

`checker/summary.md`, `checker/plan-90.md`, `checker/report.md`,
`checker/one-pager.md`. Then give the owner the verdict in one line and the one
thing to do this week.
