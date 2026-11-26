---
name: checker-customers
description: >-
  Hears what the real customers of an Indonesian business that is already open
  are saying, from two sources: the public reviews on Google Maps, GoFood,
  GrabFood, ShopeeFood, Shopee, Tokopedia/TikTok Shop and the comments on its
  TikTok and Instagram, each read, coded and linked; and a short WhatsApp survey
  of customers who used to buy and stopped. Tallies the complaints by theme with
  a tool, finds the reason people leave, what would bring them back and how many
  really would, and ties each to a fix. Nothing simulated, nothing invented. Use
  when the owner asks "why are sales dropping", "kenapa pelanggan tidak balik
  lagi", "what do customers complain about", "check my reviews", "rating turun", or
  when /checker-health shows sales falling.
argument-hint: "[--reviews-only | --survey-only]"
---

# checker-customers

A business that is already open has something an idea never has: real
customers. This skill listens to them instead of simulating them.

## The tool

```bash
python3 "${CLAUDE_SKILL_DIR}/reviews.py" --listings checker/customers/listings.csv \
  --reviews checker/customers/reviews.csv --survey checker/customers/survey.csv --out checker
```

Any one file alone works. It writes `checker/customers.json` (the health check
reads the rating) and `checker/customers-data.md` (the tables). Examples:
`listings.example.csv`, `reviews.example.csv` and `survey.example.csv` in this
folder.

## Step 1: the ratings, as the pages show them

From `checker/business.md`, find the business's own pages: its Google Maps
listing, its outlet on each delivery app, its marketplace store, its TikTok and
Instagram. Ask the owner for the links if they are not there.

For each page that shows a rating, one row in `checker/customers/listings.csv`:

`source,rating,review_count,url`

with the overall rating and the number of reviews **exactly as the page shows
them**. This is the rating the health check uses. Never use the average of the
reviews you read in step 2: you read the worst ones first, so it is biased low.

## Step 2: read the reviews

Read the most recent reviews first, up to about 50 per source; the 1 to 3 star
ones first, then the 4 stars ("enak, tapi..."). For each, one row in
`checker/customers/reviews.csv`:

`source,date,stars,theme,quote,url`

- **theme** is one short code per review, the main point: `rasa`, `porsi`,
  `harga`, `lama` (slow), `kebersihan`, `pelayanan`, `kemasan`, `salah pesanan`,
  `stok habis`, `pengiriman`, `kualitas`, `pujian` (praise). Use the same code
  for the same thing every time; add a new code only when none fits.
- **quote** is verbatim, in the language it was written, short.
- **url** is where it was read. Comments on social posts have no stars: give them
  stars only if the meaning is plain, otherwise leave them out of the CSV and
  quote them in the write-up.

Public sources only. Read pages as a person would and respect each site's
terms. If a page cannot be reached, say so. Never write a review that was not
read.

## Step 3: ask the ones who left

Reviews come from people who still care. The ones who quietly stopped are the
ones that matter for falling sales. Write the owner a WhatsApp message they can
send to 15 to 30 customers who used to buy and stopped (from the WhatsApp chats,
the regulars the staff remember, or the app's customer list where the platform's
rules allow contacting them):

```
Halo Kak [nama], ini [nama pemilik] dari [nama usaha]. Sudah lama Kakak tidak
pesan lagi, boleh saya tanya sebentar? Apa alasan utamanya? Jawab jujur saja,
tidak apa-apa, ini untuk memperbaiki usaha kami. Kalau ada yang diperbaiki,
Kakak mau coba lagi? Terima kasih banyak.
```

No discount in the first message: it buys a polite answer instead of the true
one. The owner sends it, not you. Each answer is one row in
`checker/customers/survey.csv`:

`date,last_bought,reason,would_return,what_brings_back`

- **reason**: a short code, like the themes, plus `pindah` (moved), `coba tempat
  lain` (tried another place), `tidak butuh lagi`.
- **would_return**: `ya`, `mungkin` or `tidak`. A **mungkin counts as a no**:
  Indonesian politeness makes "nanti deh" and "boleh juga" sound keener than they
  are. Only a ya counts as coming back.
- No names or phone numbers in the CSV.

Under 10 answers: say the survey is thin, and give it anyway.

## Step 4: tally and connect

Run the tool. Then write `checker/customers.md`:

1. The rating per page and overall, from the listings (never from the reviews read).
2. The complaints, ranked, with one or two linked quotes each; mark themes with
   under three reviews as thin.
3. Why people stopped buying, ranked, and how many really would come back.
4. **Connect each top complaint to the numbers.** Porsi complaints while direct
   cost rose: if portions really got smaller, the cost of each sale should have
   fallen; that it rose points at purchase prices, or stock leaving without being
   sold (the dig in `/checker-health` checks both). Lama complaints on the apps: check the
   busy hours against the roster. Harga complaints: check the competitors' prices.
   Say which skill checks it.
5. **What would bring them back**, with how many said it, and what it would cost.
6. What customers praise: the thing to protect while fixing the rest.

## Verification rules (required)

- Every review row has its link. Every survey row is a real answer the owner
  received.
- Quotes are research, never testimonials. Do not post them anywhere as praise.
- Do not reply to reviews or message customers yourself; draft, and let the owner
  send.

## Output format (fixed)

```
CUSTOMERS: [Business], reviews [period], survey [date]

Rating: x.x across n reviews, as the pages show it ([source x.x, ...])
Top complaints: [theme] (n), [theme] (n), [theme] (n)
Why they stopped: [reason] (n of N); would really come back: xx%
What brings them back: [answer] (n)

The link to the numbers: [one or two lines]
Protect: [what they praise]
```

## Output

`checker/customers/listings.csv`, `checker/customers/reviews.csv`, `checker/customers/survey.csv`,
`checker/customers.json`, `checker/customers-data.md`, `checker/customers.md`.
Rerun `/checker-health` so the rating enters the check. Next:
`/checker-competitors` if customers mention another place.
