---
name: checker-intake
description: >-
  The first step of founder-id-checker, for a business in Indonesia that is
  already open. Interviews the owner for ten minutes and reads whatever records
  exist (a POS export, the GoFood/GrabFood/ShopeeFood or Shopee/Tokopedia/TikTok
  Shop seller reports, a bank statement, a handwritten sales book typed into a
  sheet, WhatsApp order notes) and turns them into the real monthly numbers the
  other checker skills read: sales and commission per channel, direct cost,
  labour, fixed costs, PPh Final, what the owner takes, debt payments and cash on
  hand. Marks every estimate as an estimate. Use when the owner says "check my
  business", "cek bisnis saya", "is my business healthy", "usaha saya sehat
  tidak", "where is my money going", or starts the checker on a business.
argument-hint: "[path to the records, or leave blank to start with the interview]"
---

# checker-intake

Every other checker skill works from the numbers this one writes. A check-up
built on invented numbers is worse than none, so this skill asks, reads, and
labels. It never fills a gap with a guess it does not call a guess.

What the user typed after `/checker-intake`: `$ARGUMENTS`.

## Step 1: the business, in ten questions

Ask in one or two messages, not ten. Skip what the records already answer.

1. Name, what it sells, and since when it has been open.
2. Where: city and area, or online nationwide. One outlet or several?
3. Type: food and drink (`fnb`), shop (`retail`), online seller (`online`),
   service (`service`) or other (`other`).
4. Channels: walk-in, GoFood/GrabFood/ShopeeFood, Shopee, Tokopedia/TikTok
   Shop, WhatsApp, resellers, B2B. Roughly what share each?
5. Legal form (individual, PT Perorangan, CV, PT) and whether it has an NIB.
6. How many staff, on what pay, and whether the owner draws a salary.
7. What records exist, and for how many months.
8. Cash on hand today (bank plus drawer), and any loan with its monthly payment.
9. What worries the owner most.
10. What the owner wants from this: fix it, grow it, sell it, or decide whether
    to keep going.

Write `checker/business.md`:

```markdown
# <business name>

- What it is: one sentence. Open since <month year>.
- Type: fnb / retail / online / service / other.
- Where: <city, area>, <outlets>.
- Channels: <channel and rough share, ...>. Payout delay per channel, if known.
- Legal form and NIB: <...>.
- Team: <staff and roles>. Owner's salary: <amount or "none, takes cash as needed">.
- Records: <what exists, which months>.
- The owner's worry: <their words>.
- The owner's goal: fix / grow / sell / decide.
```

## Step 2: the records

Read what the owner gives. Common sources and what to take from each:

| source | take |
| --- | --- |
| POS export (Moka, Pawoon, Majoo, Olsera, iSeller, Qasir...) | gross sales per day and per channel, discounts, transactions |
| GoBiz, GrabMerchant, ShopeeFood Partner | gross sales, commission and fees, orders, promo co-funding (a discount) |
| Shopee, Tokopedia/TikTok Shop seller centre | order value, every fee line (admin, payment, programmes, affiliates), orders |
| Bank statement or mutasi | payouts received, supplier payments, rent, wages, loan payments, cash the owner moved out |
| Purchase notes, nota, supplier invoices | direct cost per month |
| Payroll sheet or notes | wages, overtime, meals, employer BPJS, THR in the month it was paid |
| A handwritten book | ask for photos or a typed copy; read it as it is |

No records at all? Use the interview: daily sales on a normal, busy and slow day,
the days open, the price and cost of the best seller, the monthly bills. Build
the months from that, label every number **(estimate)**, and offer to set up a
simple daily log so the next check-up runs on real numbers.

## Step 3: write the numbers

Write `checker/actuals.json`, one entry per full month, oldest first. Shape
(example: `${CLAUDE_SKILL_DIR}/../checker-health/example.json`):

```json
{
  "business": "Bakso Mas Yono", "type": "fnb", "currency": "IDR",
  "months": [
    {"month": "2026-11", "days_open": 30,
     "channels": {"walk-in": {"gross": 49000000, "commission": 0, "orders": 2579},
                  "GoFood/GrabFood": {"gross": 29500000, "commission": 6490000, "orders": 952}},
     "discounts": 970000, "direct_cost": 28350000, "labour": 17400000, "fixed_costs": 9750000,
     "pph_final": 403500, "other_costs": 600000, "owner_drawings": 10000000, "debt_payment": 2900000}
  ],
  "cash": {"balance": 21500000, "as_of": "2026-11-25"},
  "owner_fair_salary": 6000000,
  "targets": {"direct_cost_pct": 0.35},
  "estimates": ["Direct cost is purchases only: there is no stock count."]
}
```

The rules for each field:

- **gross** per channel is what customers paid before the platform's cut, after
  item prices, before discounts. **PBJT or PPN collected is not sales**: take it
  out.
- **Months** are YYYY-MM. A channel whose fees are over 5% of its gross counts as
  an app or marketplace; QRIS and card fees stay under that. Set
  `"platform": true` or `false` on a channel to say it outright.
- **commission** is every platform and payment fee on that channel: commission,
  admin, payment, programme, affiliate and ad fees charged per order. Ads bought
  separately go in `other_costs`.
- **discounts** are promos the business paid for, including its share of app
  promos.
- **direct_cost** = opening stock + purchases - closing stock. No stock count:
  use purchases, and add that to `estimates`.
- **labour** = wages + overtime + staff meals + employer BPJS + THR in the month
  it was paid. An owner's fixed salary goes here; cash the owner takes
  as needed goes in `owner_drawings`.
- **fixed_costs**: rent (a yearly rent counts as one twelfth each month),
  electricity, water, gas, internet, apps, accountant.
- **owner_drawings** (prive) and **debt_payment** are never business costs. They
  are kept apart so the check can say what the business keeps.
- **owner_fair_salary**: if the owner works in the business and draws no fixed
  salary in `labour`, what it would cost to hire someone to do that work (a
  kepala toko or outlet manager at the local wage). Without it, a business that
  runs on the owner's unpaid hours looks more profitable than it is. Leave it out
  if the owner's salary is already in `labour` or the owner does not work in it.
- **targets** only when the owner has their own (a recipe-costed food cost, a
  category margin). Otherwise leave it out and the defaults for the type apply.
- A month with missing days stays as it is: list the missing dates in
  `estimates`, never fill them with an average.

## Step 4: check it adds up

```bash
python3 "${CLAUDE_SKILL_DIR}/../checker-health/health.py" checker/actuals.json --check
```

If it reports an error, fix the data (never the tool) and say what changed.
Then read the totals back to the owner in three lines (net sales, costs, what is
left, for the latest month) and ask whether it matches what they feel. A
business that "always feels short" while the numbers say a large profit usually
has drawings or costs nobody wrote down: ask before going on.

## Rules

- Never invent a number. Ask, or estimate with the basis in one sentence and an
  entry in `estimates`.
- Keep the owner's records as they are. Write the clean numbers in
  `checker/actuals.json`, and note in `checker/business.md` which file each came from.
- Money in full Rupiah as plain numbers. Months as YYYY-MM.
- Sensitive data stays in the project folder. Do not paste customer names or
  phone numbers from order notes into any file.

## Output

`checker/business.md`, `checker/actuals.json`. Then say the latest month's net
sales and net profit in one line, and run `/checker-health` next.

## Where the checker goes next

```
intake -> health -> channels -> customers -> competitors -> compliance -> board -> report
```

Every skill can also run on its own; each reads whatever is already in `checker/`.
