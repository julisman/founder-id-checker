---
name: checker-compliance
description: >-
  Checks what an Indonesian business that is already open has, and has not yet
  sorted out, on permits, certificates, tax and payroll: the NIB and the right
  KBLI on OSS-RBA, PIRT, BPOM, halal certification and its deadlines, SLHS,
  signage, the trademark at DJKI, PPh Final UMKM paid on gross turnover, PBJT
  (ex-PB1) and PPN collected and paid on, the Rp4,8 miliar PKP line, UMK wages,
  BPJS, THR and overtime. Gives each item a status (ok, missing, expired, not yet
  checked) and a severity (blocks sales, a fine or sanction, advised), with the
  official page to confirm it and the order to fix them in. Holds the dated
  Indonesia reference files every checker skill reads. Use when the owner asks
  "is my business legal", "izin apa yang kurang", "do I need halal", "am I paying
  the right tax", "BPJS karyawan", or before a bank loan, a marketplace listing or
  an inspection.
argument-hint: "[topic: permits | tax | payroll | all]"
---

# checker-compliance

Most small businesses in Indonesia opened before every paper was in order. This
skill finds the gaps, ranks them by what they can cost, and gives the fix for
each. It is a checklist, not a judgement.

## The reference files

All in `${CLAUDE_SKILL_DIR}/reference/` (if that path is not expanded, use the
base directory Claude Code printed for this skill):

| file | what is in it |
| --- | --- |
| `reference/tax.md` | PPh Final UMKM, PPN and PKP, PBJT, PPh 21, what is revenue and what is a pass-through |
| `reference/permits.md` | business forms, OSS-RBA and NIB, KBLI, PIRT, BPOM, halal, SLHS, trademarks, e-commerce and advertising rules |
| `reference/payroll.md` | UMP/UMK, the micro and small business wage rule, BPJS, THR, overtime, contracts |
| `reference/payments-channels.md` | QRIS fees, e-wallets, COD, delivery apps, marketplaces, logistics |
| `reference/calendar.md` | Ramadan and Lebaran, mudik, payday, shopping festivals, rainy season |
| `reference/sources.md` | the official sites to confirm each item |

Read only the files the business needs. They are dated: anything marked *check*
changes often and must be confirmed on the official source before it goes in
the list.

## Step 1: the facts that decide what applies

From `checker/business.md` (run `/checker-intake` first if it is missing): what
it sells, where, the legal form, the yearly turnover (from `checker/actuals.json`:
twelve times the average month, or the real twelve months if there are), the
number of staff, and the channels. Ask for anything missing, at most three
questions.

## Step 2: the checklist

Go through each item that applies. Ask the owner for the number or the document
(NIB, certificate number, last tax payment receipt, BPJS registration) rather
than taking "sudah" on trust; an item with no number is `unknown`.

| area | items |
| --- | --- |
| Registration | NIB on OSS; the KBLI matches what is really sold (a café selling packaged products online may need a second one); risk level and the permits it triggers |
| Product | PIRT for home-made packaged food; BPOM for the categories that need it and anything sold beyond PIRT's limits; halal certification and the deadline for the category; SLHS for food service where the region requires it; labels |
| Place | the building and signage permits the region asks for; zoning for the street |
| Brand | the trademark filed at DJKI, or at least searched on PDKI |
| Tax | PPh Final 0.5% paid monthly on gross turnover (before the apps' cut); PBJT collected and paid on, if the region requires it; turnover against the Rp4,8 miliar PKP line; PPh 21 withheld for staff where it applies; records of monthly turnover |
| Staff | wages against the UMK or a written agreement under the micro and small business rule; BPJS Kesehatan and Ketenagakerjaan registered and paid on the real wage; THR paid in full and on time; overtime paid; written contracts |
| Channels | the marketplace and delivery-app rules for the category (some ask for BPOM or halal before listing); consumer and personal data rules for WhatsApp broadcasts |

**Severity** for each item:

- `blocks_sales`: without it the business can be stopped, delisted or refused
  (a marketplace delisting a product with no BPOM number, a closure order).
- `penalty`: a fine, interest or sanction, or a claim from a worker.
- `advised`: no sanction now, but it protects the business or opens doors (a
  trademark, a bank loan, a corporate client).

## Step 3: write it down

`checker/compliance.json`, which the health check reads:

```json
{"checked": "2026-11-26", "items": [
  {"item": "NIB", "status": "ok", "severity": "blocks_sales", "note": "NIB 1234..., KBLI 56103", "source": "https://oss.go.id"},
  {"item": "Halal certificate", "status": "missing", "severity": "advised", "note": "micro business: required by 17 October 2028 (reference/permits.md, check); free self-declare route", "source": "https://halal.go.id"},
  {"item": "BPJS Ketenagakerjaan", "status": "unknown", "severity": "penalty", "note": "owner not sure all 4 staff are registered", "source": "https://bpjsketenagakerjaan.go.id"}
]}
```

`status` is one of `ok`, `missing`, `expired`, `unknown`. `severity` is one of
`blocks_sales`, `penalty`, `advised`. Then `checker/compliance.md`: the list
grouped by severity, each item with what to do, where (the office or website),
roughly how long it takes and what it costs (free where it is free, such as the
NIB and halal self-declare for eligible micro businesses), and the official link
with the date checked.

Order the fixes: `blocks_sales` first, then `penalty` by size, then `advised`.
Free and fast items go first within each group.

## Rules

- Regional rules differ: PBJT, UMK, signage and zoning are set by the province,
  regency or city. Name the region and its regulation.
- Never present a remembered rate or deadline as current. If the official page
  cannot be reached, give the dated figure from the reference file and mark it
  *to confirm*.
- Back taxes and back pay are a conversation for a konsultan pajak or Disnaker,
  not a number to estimate here. Say so when an item is missing for months.
- Not legal or tax advice. Say once that a konsultan pajak, a notary or the
  relevant office (KPP, DPMPTSP, Disnaker, BPJPH, BPOM) confirms it.

## Output

`checker/compliance.json`, `checker/compliance.md`. Rerun `/checker-health` so
the gaps enter the check. Next: `/checker-board`.
