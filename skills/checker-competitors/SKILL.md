---
name: checker-competitors
description: >-
  Checks what has changed around an Indonesian business that is already open:
  who opened nearby or on the same apps and marketplaces since it started, who
  closed, what they charge on each channel against this business's prices, how
  they are rated, what promos they run, and what their customers complain about.
  Includes the informal competitors (the warung, the kaki lima, the home seller on
  WhatsApp, the reseller on Shopee) and the substitutes. Public sources only,
  every fact linked. Ends with where the business stands now and what to defend
  or change. Use when the owner says "a new place opened next door", "kompetitor
  baru", "are my prices too high", "why is that place busier", "who am I losing
  customers to", or when /checker-customers shows people going elsewhere.
argument-hint: "[area or channel, default from checker/business.md]"
---

# checker-competitors

An open business already has a position. This skill checks whether it still
holds, from the buyer's side of the screen.

## The rules

- **Public sources only, every fact linked.** Google Maps listings, delivery-app
  menus, marketplace listings and ratings, Instagram and TikTok profiles, news.
  If a source cannot be reached, say so. Never invent a competitor, a price, a
  rating or a review.
- **Read, do not scrape.** Read pages as a person would. Respect each site's terms.
- **Price and channel together.** The same item costs more on GoFood than at the
  counter, and a marketplace price may include a voucher. Say which.
- Quotes verbatim with the link. They are research, never material to attack a
  competitor with.

## Step 1: who is there now

From `checker/business.md` (run `/checker-intake` first if it is missing), search
the way a buyer near the business would: the map for the area, each delivery app
from the business's address, the marketplaces and TikTok for online sellers
("<thing> murah", "<thing> terdekat", "<thing> terbaik").

| type | what it means |
| --- | --- |
| Direct | sells the same thing to the same buyer, within reach |
| Indirect | a different product for the same need |
| Informal | small, unregistered or home-based sellers buyers really use |
| Substitute | how buyers solve it without a business |

Aim for 5 to 10 direct and indirect. Ask the owner which ones they see taking
their customers, and which opened since the business started; check the
listing's first reviews to date an opening when the owner is not sure.

## Step 2: the facts

One row per competitor in `checker/competitors.csv`:

`name,type,url,location_or_channel,distance_or_rank,comparable_item,price,price_channel,rating,review_count,promo_now,trust_signals,opened,source_date`

- `comparable_item` and `price`: the item closest to this business's best seller.
  Put this business in the table too, from its own listings, so the comparison is
  like for like.
- `promo_now`: the promo they run on that channel today, as shown.
- `opened`: the month, if known, or `before` if it was there when this business
  opened.

## Step 3: what their customers say

For the 3 that matter most, read their recent 1 to 3 star and 4 star reviews.
Note the themes with counts and a linked quote each. Then compare with this
business's own themes in `checker/customers.md`, if it exists: a complaint this
business has and they do not is a weakness; one they have and this business does
not is something to say out loud.

## Step 4: where the business stands

Write `checker/competitors.md`:

1. The table, sorted by how directly each competes, this business included.
2. Price: this business against the lowest, median and highest, by channel.
3. A text positioning map on the two axes this buyer cares about most (price and
   portion, price and speed, quality and trust...), with this business on it.
4. **What changed** since the business opened: who came, who left, who cut prices.
5. **What to defend**: what this business still does better, with the evidence.
6. **What to change**: where it now loses, and the one move that answers it
   (a price, a product, a channel, a promise). If the honest answer is that a
   competitor does the same thing better and cheaper, say so plainly.

## Output format (fixed)

```
COMPETITORS: [Business], [area/channels], checked [date]

This business: [item] Rp xx.xxx (counter) / Rp xx.xxx (app), rating x.x
Market: lowest Rp xx.xxx, median Rp xx.xxx, highest Rp xx.xxx ([channel])
New since opening: [names, month]
Defend: [one line, with the evidence]
Change: [one line, with the evidence]
```

## Output

`checker/competitors.csv`, `checker/competitors.md`. Next: `/checker-board` to
decide what to do about it, or `/checker-report`.
