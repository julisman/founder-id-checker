# founder-id-checker

Nine Claude skills that check a business in Indonesia that is already open.
Free, MIT, no signup, no API key, nothing to connect. Numbers in Rupiah, rules
from Indonesia, any kind of business: food and drink, retail, online sellers,
services.

It answers the questions owners actually ask: *usaha saya sehat tidak?* Where
does the money go? Why are sales dropping? Are the apps worth it? Which papers am
I missing? Should I open a second outlet, fix what I have, or stop?

Every answer comes from the business's own records and its real customers. The
verdict at the end is computed from the numbers, never written by hand:
**Sehat** (healthy), **Waspada** (watch out) or **Kritis** (critical).

## Install

As a plugin, in Claude Code:

```
/plugin marketplace add julisman/founder-id-checker
/plugin install founder-id-checker@founder-id-checker
```

Installed as a plugin the skills show up as `/founder-id-checker:checker-intake`
and so on. Copy the folders instead if you want plain `/checker-intake`:

```bash
git clone https://github.com/julisman/founder-id-checker.git
cp -r founder-id-checker/skills/checker-* ~/.claude/skills/
```

Copy all the folders: several skills read the tools in `checker-health` and the
reference files in `checker-compliance`. The tools need Python 3.8 or newer.
Nothing to pip install.

## The nine

| command | job | what it does |
| --- | --- | --- |
| `/checker-intake` | Intake | A ten-minute interview plus whatever records exist (POS export, delivery-app and marketplace reports, bank statement, a handwritten book) turned into real monthly numbers per channel. Every estimate is labelled. |
| `/checker-health` | Health check | Net profit, break-even, the trend, direct cost and labour against targets, what the owner takes against what the business earns, debt, cash in weeks, platform dependence. A computed verdict, fixes ranked by Rupiah a month, and a field check of the biggest cost problem. |
| `/checker-channels` | Channels | What every channel really leaves from each Rp100.000 after the platforms' fees, whether the promos pay for themselves, the cash stuck in payouts, and a plan to move repeat buyers to direct orders. |
| `/checker-customers` | Customers | Real reviews from Google Maps, the delivery apps and the marketplaces, coded and linked, plus a WhatsApp survey of customers who stopped buying. Why they leave, how many would really come back, and the link to the numbers. |
| `/checker-competitors` | Competitors now | Who opened, closed or cut prices since the business started, prices per channel side by side, their ratings and complaints, what to defend and what to change. |
| `/checker-compliance` | Papers and tax | NIB and KBLI, PIRT, BPOM, halal and its deadline, SLHS, the trademark, PPh Final, PBJT, the PKP line, UMK, BPJS, THR. Each item ok, missing or unknown, ranked by what it can cost. Holds the dated Indonesia reference files. |
| `/checker-board` | Board | Four sub-agents, one per lens (Money, Customer, Position, Local market), read the evidence and vote GROW, FIX, PIVOT or CLOSE, and answer the decision on the table. |
| `/checker-report` | Report | The check-up with its computed verdict, the top 3 fixes, a 90-day plan with a number and a date for every action, and a one-pager for a partner or a bank. |
| `/checker-simulate` | What-if panel | Tries a planned change (a price, a menu item, a bundle, a win-back message) on a simulated panel of 30 personas (or any number you ask for) drawn from the real reviews, the real reasons customers left and the real channel mix, against what is there now. Labelled SIMULATED, never part of the verdict, and it always ends with the cheap real test to run. |

## How to use it

```
intake -> health -> channels -> customers -> competitors -> compliance -> board -> report
```

Each skill reads what the others wrote, in a `checker/` folder in your project.
Each can also run on its own. Run the whole check again every 90 days with the
new months and compare the verdicts.

`/checker-simulate` sits outside the line: run it after `/checker-customers`
whenever the owner wants to try a change before testing it on real customers.

An example: Bakso Mas Yono, a bakso stall on Margonda in Depok, open since March
2024, with walk-in, GoFood/GrabFood and ShopeeFood. Six months of numbers are in
`skills/checker-health/example.json`, and example listings, reviews and survey answers in
`skills/checker-customers/`.

1. **`/checker-intake`** turns the POS export, the GoBiz and ShopeeFood reports
   and the purchase notes into `checker/actuals.json`. There is no stock count,
   so direct cost is marked as an estimate.
2. **`/checker-health`** says **Waspada**. Net profit is Rp17.516.067 a month
   (23.6%) and the business is 63% above break-even, but net sales fell 7.2% from
   the quarter before, direct cost climbed every month to 38.5% against a 35%
   target, and the Rp21.500.000 in cash covers 1.6 weeks of running costs. After
   the owner's Rp10.000.000 and the loan's Rp2.900.000, the business keeps
   Rp4.616.067 a month. Paying someone Rp6.000.000 to do the owner's work would
   still leave Rp11.516.067, so the profit is real, not the owner's unpaid wage.
3. **`/checker-customers`** reads the listings: 4.2 overall across 1.647 reviews,
   lowest on GoFood at 4.1. The worst recent reviews point at slow app orders and
   smaller portions. Of 8 customers who stopped, 3 would really come back. Smaller
   portions while direct cost rose sends the owner back to check purchase prices.
4. The top fix, ranked by the tool: win back the lost sales (up to Rp3.521.061 a
   month), then direct cost (up to Rp2.594.110), then moving app buyers to direct
   orders (up to Rp1.442.333).

## The tools

Four of them, all standard-library Python. None touch the network.

```bash
python3 skills/checker-health/health.py checker/actuals.json            # the checks, the verdict, the fixes
python3 skills/checker-customers/reviews.py --listings checker/customers/listings.csv --reviews checker/customers/reviews.csv --survey checker/customers/survey.csv --out checker
python3 skills/checker-report/compile.py --dir checker                  # the report with its verdict
python3 skills/checker-simulate/simulate.py panel --customers checker/customers.json --actuals checker/actuals.json --n 30 --out checker/simulate/run
```

**`health.py`** reads one JSON of real monthly numbers. It keeps the platforms'
commission apart from sales, the owner's drawings and debt payments apart from
costs, and computes break-even from the business's own cost structure. A missing
field is an error, never a guess. `--check` exits 0 for Sehat, 1 Waspada, 2
Kritis, 3 Incomplete, so it can run in a routine.

**`reviews.py`** tallies coded reviews and survey answers. The rating comes from
what each listing shows, never from the reviews read (those are read worst-first
to find complaints). Every row needs its link; a *mungkin* (maybe) counts as a no.

**`simulate.py`** builds the what-if panel from the real complaint themes, lapse
reasons and channel mix, and tallies the persona answers per variant against the
baseline (a *mungkin* is a no; a lead under 10 points is too close to call).

**`compile.py`** assembles the report and rebuilds the numbers section from the
actuals every time, so the report can never disagree with its own verdict.

```bash
python3 -m unittest discover -s tests -v
```

## The dashboard

A local, read-only web page of everything in `checker/`, updating by itself
while the skills run: the verdict with every check (problems first), the key
numbers, net sales against break-even and what the business keeps month by
month, direct cost and labour against their targets, where every Rp100.000
goes, the fixes ranked in Rupiah, what each channel keeps, the listing ratings,
the complaints and why customers left, the papers by severity, the board's
vote, and every document. In Indonesian or English (the ID/EN button; it
starts in the browser's language and remembers the choice), light or dark, with
a table behind every chart. Every check and fix comes from `health.py` in both
languages; documents show in the language the skills wrote them in.

```
/founder-id-checker:checker-gui                          # from Claude Code; /founder-id-checker:checker-gui-stop ends it
python3 gui/serve.py --dir path/to/project               # or from a terminal: http://127.0.0.1:8765
python3 gui/serve.py --dir path/to/project --export check-up.html   # one offline file to send to a partner or a bank
python3 gui/demo.py /tmp/checker-demo                    # a demo project (Bakso Mas Yono) to try it on
```

Standard library only, no internet, listens on 127.0.0.1 only, answers no
request that would change a file, and never shows a file outside a fixed list.
The numbers come from `health.py`, so the page can never disagree with the
report.

## Fine print

**The board lenses are the checker's own checklists.** They are not summaries of
any book and speak for no one.

**Nothing in the check-up is simulated.** Customers are real reviews with links
and real answers the owner received. The skills never write a review, a quote or
an answer. The one exception is `/checker-simulate`, a labelled what-if: its
panel is drawn from the real evidence, everything it writes says SIMULATED, and
the health check, the board, the report and the dashboard never read it. It
picks which change to test for real; it never proves one works.

**Indonesian rules change.** Tax rates, the halal deadlines, QRIS fees, platform
commissions and minimum wages all changed in 2025 and 2026. The reference files
in `skills/checker-compliance/reference/` are dated, and the skills confirm
current figures on the official sources before using them.

**The numbers are only as good as the records.** Every estimate is marked. Check
the structure, payroll and tax with an accountant or konsultan pajak.

**Research uses public sources, with links.** No scraping against a site's terms.

**Not financial, legal or tax advice.** The skills tell you what to check and
where; a professional confirms it.

## Files

```
skills/checker-intake/       SKILL.md
skills/checker-health/       SKILL.md, health.py, example.json
skills/checker-channels/     SKILL.md
skills/checker-customers/    SKILL.md, reviews.py, listings.example.csv, reviews.example.csv, survey.example.csv
skills/checker-competitors/  SKILL.md
skills/checker-compliance/   SKILL.md, reference/ (tax, permits, payroll, payments-channels, calendar, sources)
skills/checker-board/        SKILL.md, lenses.md
skills/checker-report/       SKILL.md, compile.py
skills/checker-simulate/     SKILL.md, simulate.py
gui/                         the dashboard (serve.py, state.py, demo.py, static/)
commands/                    /checker-gui and /checker-gui-stop
tests/                       the tests for every tool, the dashboard and the repo
```

Your own files live in `checker/` in your project.

## License

MIT
