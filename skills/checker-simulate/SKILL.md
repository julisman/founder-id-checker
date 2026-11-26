---
name: checker-simulate
description: >-
  Tries a planned change on a simulated panel of the business's own customers
  before the owner spends money testing it for real: a new price, a menu or
  product change, a bundle or promo, a new channel, a WhatsApp message to win
  back lapsed customers. The panel (30 personas by default, any number the owner
  asks for) is drawn from the real evidence the checker gathered: the complaint
  themes and quotes from the real reviews, the reasons real lapsed customers gave
  and the real channel mix and average ticket. Each persona is played by a
  sub-agent built to resist the polite yes ("boleh juga", "nanti deh"); a mungkin
  counts as a no. Compares the change with what is there now, says which option
  to test for real and designs that cheap real test. Everything it writes is
  labelled SIMULATED and never enters the health check, the board or the report.
  Use when the owner asks "kalau harga naik, pelanggan kabur tidak", "would
  customers like this", "test this to customers first", "simulate customers",
  "coba dulu ke pelanggan", or before changing a price, a menu or a promo.
argument-hint: "[the change to test] [optional panel size, e.g. 50 persona]"
---

# checker-simulate

The checker's what-if. Everything else in the checker comes from real records
and real customers; this skill is the one place something is simulated, so it is
fenced off: it answers "which change is worth testing for real?", never "is the
business healthy?".

What the user typed after `/checker-simulate`: `$ARGUMENTS`.

## Step 0: what to test, how many, and the evidence

**The change.** Read it from `$ARGUMENTS`. If there is none, ask the owner what
they are thinking of changing. Up to three options can be tested at once.

**The panel size.** 30 personas unless the owner asked for another number. Read
it from `$ARGUMENTS` or the conversation: "50 persona", "100 orang", "panel 80",
"--n 40" and the like all set it. Any whole number from 1 is accepted. Under 20,
say the panel is thin before running it; above 200, say the run will take a
while and launch it anyway if the owner confirms.

**The evidence.** The panel needs `checker/customers.json` with reviews or a
survey in it. If it is missing, stop and run `/checker-customers` first: without
real customers there is nothing to draw the panel from, and this skill never
invents a target market. Also read `checker/actuals.json` (channels and average
ticket), `checker/business.md` and, if they exist, `checker/customers.md` and
`checker/competitors.md`.

Each run lives in its own folder, `checker/simulate/<YYYY-MM-DD>-<short-slug>/`
(for example `checker/simulate/2026-11-26-harga-naik-2000/`), so earlier runs are
kept. Call it `<run>` below.

## Step 1: the test card

Write `<run>/test.md`: the options exactly as a customer would meet them.

- **Variant A is always what is there now**: today's price, menu, offer or
  message. Simulated buyers say yes too easily; the change only counts if it
  beats the baseline on the same panel.
- **B (and C)** are the change: the new price per channel (with the app's
  markup where there is one), the new item with its portion and price, the
  bundle, the exact WhatsApp message the owner would send. Concrete and in
  Indonesian, as it would appear on the menu, the app or the chat.
- What the customer cannot see (the owner's margin, the reason for the change)
  stays out of the card.

## Step 2: the panel

```bash
python3 "${CLAUDE_SKILL_DIR}/simulate.py" panel --customers checker/customers.json \
  --actuals checker/actuals.json --n <size> --out <run>
```

It writes `<run>/panel.json`: one slot per persona with a status (current
customer or lapsed), the concern they bring (a real review theme or a real reason
for leaving, in proportion to how often it came up), the channel they order on
(in proportion to the real sales mix) with its average ticket, and where there is
one, the real review quote the persona is grounded in. Half the panel is lapsed
by default; pass `--lapsed-share` (0 to 1) when the change is aimed at one group,
for example `--lapsed-share 1` for a win-back message.

## Step 3: the persona sub-agents

Split the personas into batches of 10 (the last batch may be smaller). Launch
one sub-agent per batch (Agent tool, `subagent_type: general-purpose`), up to 10
in ONE message; for more batches, launch the next 10 when those finish.
**Sub-agents cannot see this conversation**, so each gets a brief that stands on
its own:

```
You are playing <k> customers of <business> (<type>, <place>). Read <run>/test.md
and the personas <P01..P10> in <run>/panel.json. For each persona, write a
one-line life (age, work, monthly income in Rupiah, where they live, how often
they buy here) consistent with the channel, average ticket and concern given,
then answer each variant in test.md AS THAT PERSONA, once per variant.

Rules:
- Stay in character. A persona whose concern is "porsi" checks the portion
  first; a lapsed one who left over "harga" has a price in mind and a place they
  go now; a "pujian" regular mostly wants nothing changed.
- Habits win. Saying yes means actually buying this week at that price on that
  channel. If they would not change what they do, it is tidak.
- "Boleh juga", "nanti deh", "lihat dulu" are mungkin, and mungkin is not a yes.
  Do not be polite to the owner.
- Never say yes to every variant out of kindness. If two variants are the
  same to this person, give them the same answer.

Write <run>/answers-<n>.csv with the header
persona,variant,decision,reason,would_pay
one row per persona per variant: decision is ya, mungkin or tidak; reason is a
short code (harga, porsi, rasa, lama, ongkir, tidak butuh, sudah pindah, ...),
required for mungkin and tidak; would_pay is the most they would pay in Rupiah
for the main item, or empty. Then write <run>/voices-<n>.md: for each persona
the one-line life and one sentence in their own words per variant.
```

Fill in the business, type and place from `checker/business.md`, the full path
of `<run>`, and the persona ids of the batch.

## Step 4: tally

```bash
python3 "${CLAUDE_SKILL_DIR}/simulate.py" tally --panel <run>/panel.json \
  --answers <run>/answers-*.csv --out <run>
```

It refuses a persona that is not in the panel, a variant with missing answers, a
no without its reason and a decision that is not ya, mungkin or tidak; fix the
batch and rerun. It writes `<run>/simulate.json` and `<run>/simulate-data.md`:
the would-buy rate per variant (a mungkin counts as a no), by status, channel
and concern, the reasons for no, the median price the yes personas named, and
whether the lead is too close to call (under 10 points, or under 20 personas a
variant).

## Step 5: the write-up and the real test

Write `<run>/simulate.md` and copy it to `checker/simulate.md` (the latest run):

1. The label on the first line, as the tool gives it: **SIMULATED: a what-if
   panel, not real customers.**
2. What was tested and on whom: the variants, the panel size, current against
   lapsed, and the evidence it was drawn from.
3. The result per variant, against the baseline. If the lead is too close to
   call, say so and do not pick a winner.
4. Who moves and who does not: the segments that react most, marked thin under
   five personas. A change that wins the lapsed but loses the regulars is a
   different decision from one that wins both.
5. The reasons for no, ranked, with two or three persona sentences from the
   voices files, each marked as simulated.
6. **The real test.** The cheapest way to check the result on real customers
   before changing anything for everyone, with how many people, how long, the
   number that would confirm it and the date to decide. For example: send
   message B to 20 lapsed customers on WhatsApp and count orders within 7 days;
   run the new price for one weekend on GoFood only and compare orders with the
   weekend before; put the bundle on the counter menu for a week. The owner
   runs it, and real answers go through `/checker-customers` (the survey) or the
   next `/checker-intake` (the sales).

## Verification rules (required)

- Every file this skill writes carries the SIMULATED label. Persona sentences
  are never quoted as customer words, never posted as testimonials and never
  written into `checker/customers/`.
- The panel comes from `checker/customers.json`. Never run without it, and never
  add a concern, a channel or a price no real record shows.
- `/checker-health`, `/checker-board` and `/checker-report` do not read anything
  this skill writes. A simulated rate is never a reason for a verdict, only for
  which real test to run.
- Never message customers yourself; draft, and let the owner send.

## Output format (fixed)

```
SIMULATED: [Business], [what was tested], [n] personas ([x] current, [y] lapsed), [date]

A (now): xx% would buy | B: xx% | C: xx%   (a mungkin is a no)
Best: [variant], +n points over A [or: too close to call]
Moves most: [segment] (xx% to xx%)  Holds back: [reason] (n)
Price the yes personas named: Rp[median]

The real test: [what, with how many, for how long, the number that confirms it, decide by date]
```

## Output

`<run>/test.md`, `<run>/panel.json`, `<run>/answers-*.csv`, `<run>/voices-*.md`,
`<run>/simulate.json`, `<run>/simulate-data.md`, `<run>/simulate.md` and
`checker/simulate.md`. Next: run the real test, then `/checker-customers` or
`/checker-intake` with what really happened.
