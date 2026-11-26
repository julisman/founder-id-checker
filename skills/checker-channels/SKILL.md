---
name: checker-channels
description: >-
  Checks where the sales of an Indonesian business that is already open come
  from and what each channel really leaves: walk-in and the counter, QRIS and
  e-wallets, GoFood/GrabFood/ShopeeFood, Shopee, Tokopedia/TikTok Shop,
  WhatsApp orders, resellers and B2B. For each channel: gross sales, every fee the
  platform takes, what is kept from every Rp100.000, orders and the average
  order, how long the money takes to arrive, and how dependent the business is on
  it. Compares app prices with counter prices, checks whether the business's own
  promos pay for themselves, and gives a plan to move repeat buyers to direct
  orders. Use when the owner asks "is GoFood worth it", "the apps take too much",
  "should I join ShopeeFood", "komisi", "which channel makes money", or when
  /checker-health flags the platforms.
argument-hint: "[channel to look at, or leave blank for all]"
---

# checker-channels

A sale through an app is not the same sale as one at the counter. This skill
puts every channel side by side in Rupiah, from the owner's real reports.

## The data

The channel table comes from the health tool:

```bash
python3 "${CLAUDE_SKILL_DIR}/../checker-health/health.py" checker/actuals.json --channels
```

It shows, for the last three months on average: gross sales, share, commission
and its rate, what is kept from every Rp100.000, orders and the average order.
No `checker/actuals.json` yet: run `/checker-intake` first.

Then ask for, or read from the seller centre reports:

| what | where it comes from |
| --- | --- |
| The fee lines per platform (commission, admin, payment, programmes, affiliates, ads) | GoBiz, GrabMerchant, ShopeeFood Partner, Shopee Seller Centre, TikTok Shop Seller Center |
| The promos the business co-funds on each app | the same reports, promo or campaign section |
| App prices against counter prices for the 5 best sellers | the menu or catalogue on each app, and the counter price list |
| Payout delay per channel | the payout history; the bank statement |
| How many app buyers are repeat buyers | the app's customer report, if it has one |

Fee rates change several times a year. Use the rate on the owner's own report;
compare with `${CLAUDE_SKILL_DIR}/../checker-compliance/reference/payments-channels.md`
and say where the report and the reference differ.

## Step 1: what each channel leaves

For each channel, from the owner's numbers:

1. **Kept from every Rp100.000** of gross (from the table), then minus the
   direct cost of what was sold. A channel can sell a lot and leave little.
2. **Promos that pay for themselves?** For each co-funded promo, compare the
   orders in the promo weeks with the weeks before. If the extra orders times
   what each leaves is less than the business's share of the promo, it lost
   money. Say so with the numbers. Mark it thin when there are under 4 weeks.
3. **App mark-up.** If app prices equal counter prices, every app order earns
   less than a counter order by the full commission. A common fix is an app price
   that covers it; check what the closest competitors charge on the same app
   first (`/checker-competitors`).
4. **Cash timing.** Payout delay times daily app sales is cash the business has
   earned but cannot spend yet. Name the amount.

## Step 2: dependence

From the health check: the share of gross through apps and marketplaces. Above
60% one fee rise or a drop in the app's ranking hits most of the business. Work
out what a 5-point commission rise would cost a month, in Rupiah, from the
owner's own app sales.

## Step 3: the plan

Pick the two or three moves the numbers support, each with its Rupiah a month
and how to measure it:

- **Move repeat buyers to direct orders.** A card in every app order with the
  WhatsApp number and a small reason to order direct (a free topping, a pick-up
  price). Never break the platform's rules on contacting its buyers: check the
  platform's own merchant terms and cite them.
- **Reprice the app menu** to cover the commission, item by item.
- **Stop a promo that loses money**, or narrow it to slow hours.
- **Add or drop a channel.** Adding one: the commission, the setup, the packaging,
  who handles the orders. Dropping one: the orders lost, against the commission
  saved.

## Verification rules (required)

- Every number comes from `checker/actuals.json` or a seller report the owner
  gave. Name the report and the period.
- A fee rate from the reference file or memory is a guess until it matches the
  owner's report: say which.
- Do not count PBJT or PPN collected through an app as sales.

## Output format (fixed)

Write `checker/channels.md`:

```
CHANNELS: [Business], [period]

[the channel table from the tool]

What each channel leaves after fees and direct cost, from every Rp100.000:
- [channel]: Rp xx.xxx

Dependence: [share]% through apps and marketplaces. A 5-point commission rise
costs Rp x.xxx.xxx a month.
Cash waiting in payouts: about Rp x.xxx.xxx at any time.

Promos: [each one, paid for itself or not, with the numbers]

THE PLAN
1. [move], up to Rp x.xxx.xxx a month, measured by [number]
2. ...
```

## Output

`checker/channels.md`. Next: `/checker-customers` to hear what buyers on each
channel say, or `/checker-report` to put it together.
