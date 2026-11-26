---
name: checker-health
description: >-
  The financial health check for a business in Indonesia that is already open.
  Reads the real monthly numbers from checker/actuals.json and computes, with a
  tool and never by hand: net profit and margin, net sales against break-even,
  the trend of the last three months, direct cost (food cost, COGS) and labour
  against their targets, what the owner takes (prive) against what the business
  earns, debt payments, cash on hand in weeks of running costs, and how much of
  the business runs through apps and marketplaces. Gives a verdict (Sehat,
  Waspada, Kritis) and the fixes ranked by Rupiah a month, then digs into the
  biggest cost problem. Use when the owner asks "is my business healthy", "untung
  atau tidak", "why is there never any money", "where does the money go", or
  after /checker-intake.
argument-hint: "[path to actuals.json, default checker/actuals.json]"
---

# checker-health

The numbers part of the check-up. The tool does the arithmetic and the verdict;
this skill reads it to the owner in plain words and digs into the biggest
problem.

## The tool

```bash
python3 "${CLAUDE_SKILL_DIR}/health.py" checker/actuals.json
```

writes `checker/health.md` and `checker/health.json`. `--check` prints the
verdict and the checks only; `--channels` prints the channel table. If the path
is not expanded, use the base directory Claude Code printed for this skill. No
`checker/actuals.json` yet: run `/checker-intake` first.

## What it checks

Each check is ok (✓), a warning (!) or critical (✗), computed from the average
of the last three months (or fewer, if fewer exist):

| check | warning | critical |
| --- | --- | --- |
| Net margin | under the healthy margin (default 10%) | a loss |
| Break-even | under 10% above it | below it |
| Trend | net sales down 5% or more against the 3 months before | down 15% or more |
| Direct cost | over target | over target by 5 points |
| Labour | over target | over target by 5 points |
| Owner | takes more than the business earns after debt | takes anything while it earns nothing |
| Owner's pay | the profit is smaller than what the owner's own work would cost to hire (`owner_fair_salary`) | |
| Debt | payments take over half the profit | payments are more than the profit |
| Cash | under 2 weeks of running costs | under 1 week, or shrinking with under 3 months left |
| Platforms | apps and marketplaces over 60% of gross sales | |
| Customers | listing rating under 4.2, or under 10 reviews | under 3.5 (caps the verdict at Waspada) |
| Compliance | an item with a fine is missing, or not yet checked | an item selling needs is missing |

Default targets by type (the owner's own targets in `actuals.json` win):

| type | direct cost | labour |
| --- | ---: | ---: |
| fnb | 35% | 25% |
| retail | 70% | 15% |
| online | 65% | 15% |
| service | 30% | 40% |
| other | none: ask the owner | none |

The verdict: **Kritis** if any check is critical, **Waspada** if any is a
warning, **Sehat** if all pass. Never write a verdict by hand and never round a
failing number into a passing one.

## Step 1: run it and read it out

Give the owner, in this order:

1. The verdict in one line.
2. The plain-words line: of every Rp100.000 of net sales, where it goes.
3. The failed checks, worst first, each with its number.
4. **What the business keeps** after the owner and the debt. This is the line
   most owners have never seen, and it explains "untung tapi uangnya tidak ada".
5. The top fix with its Rupiah a month.

## Step 2: dig into the biggest cost problem

If direct cost or labour failed, do the field check here; do not stop at the
percentage.

**Direct cost over target.** Split it into price and use:

1. Price: compare the latest purchase price of the 5 biggest items with three
   months ago (the nota or the supplier's invoices). A price rise is a pricing
   problem, not a waste problem: the fix is the selling price or the supplier.
2. Use: for the best seller, cost one unit from the recipe or bill of materials
   (or the purchase price for resale), times the units sold, against what was
   bought. A gap over 5% is waste, portions, spoilage or missing stock.
3. Give the owner one check for tomorrow: weigh 10 portions, count the stock of
   the top item at closing two nights running, or compare the stock card with
   the shelf. Never accuse a person; describe a gap and how to measure it.

**Labour over target.** Ask for the busy hours (from the POS or app orders by
hour) and the roster. Name the hours with more staff than orders need and the
hours with too few. Changes to contracts or pay go through the rules in
`${CLAUDE_SKILL_DIR}/../checker-compliance/reference/payroll.md`.

**The owner takes more than it earns.** Propose a fixed owner's salary the
business can afford (what it earns after debt, minus a cash buffer) and a
separate account or drawer for the business. This is the single most common
fix for a small business that "never has money".

Write what you found under `## Dig` at the end of `checker/health.md` (after the
tool's output; rerunning the tool rewrites the file, so add it again after a rerun).

## Verification rules (required)

- Every number traces to `checker/actuals.json`; every input traces to the
  owner's records as noted in `checker/business.md`.
- Say "(includes estimates)" whenever the verdict rests on estimated months, and
  name the estimate that matters most.
- A trend across Ramadan, Lebaran or the rainy season is the calendar first:
  check `${CLAUDE_SKILL_DIR}/../checker-compliance/reference/calendar.md` before
  calling it a decline.
- If the owner says the business is fine and the numbers say otherwise, show the
  numbers and ask what may be missing. Do not go along.

## Output format (fixed)

```
HEALTH CHECK: [Business], [first month] to [last month]

Verdict: [Sehat / Waspada / Kritis] [(includes estimates)]

Of every Rp100.000: Rp xx.xxx materials, Rp xx.xxx wages, Rp xx.xxx rent and bills,
Rp xxx tax, Rp xx.xxx profit.
Kept by the business after the owner and the debt: Rp x.xxx.xxx a month.

FAILED CHECKS
✗/! [check]: [number and what it means]

TOP FIX
[fix], up to Rp x.xxx.xxx a month. Next: [skill]

1 NUMBER TO DOUBLE-CHECK
[the estimate the verdict depends on most, and how to check it]
```

## Output

`checker/health.md`, `checker/health.json`. Next: `/checker-channels` if the
apps and marketplaces carry much of the business, `/checker-customers` if sales
are falling.
