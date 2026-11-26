# Tax for a small business in Indonesia

Checked November 2026. Items marked *check* change often: confirm on pajak.go.id
before money moves. Not tax advice.

## What is revenue and what is not

- **Revenue** is what the business keeps from the sale. Net sales in
  `checker/actuals.json` is this number.
- **PBJT (ex-PB1) and PPN collected from the customer are not revenue.** They are
  added on top of the price and paid on to the government. Do not count them as
  sales, and do not count paying them as a cost. Do show the customer price
  including them, because that is what the buyer compares.
- **PPh Final UMKM is a cost** on gross turnover. In `checker/actuals.json` it is
  `pph_final`, 0.5% of gross turnover each month.

## PPh Final UMKM (income tax on turnover)

- 0.5% of gross monthly turnover (peredaran bruto), for businesses with turnover
  up to Rp4,8 miliar a year. Basis: PP 55/2022 as amended by **PP 20/2026**
  (enacted 22 April 2026).
- **Individuals and PT Perorangan**: under PP 20/2026 they can use the 0.5% rate
  with no time limit while they meet the criteria (per DJP). *check*
- **Individuals**: the first Rp500 juta of turnover in a year is not taxed (PP
  55/2022).
- **CV, firma, cooperatives, PT**: the rate is time-limited. *check* the current
  limits in PP 20/2026.
- Paid by the 15th of the next month; reported through Coretax. For individuals
  the NIK now works as the NPWP.
- A business can choose the normal regime instead (tax on profit). For a
  low-margin, high-turnover business, the accountant should compare.

## PPN (VAT) and the PKP threshold

- A business must register as PKP (pengusaha kena pajak) and charge PPN once
  turnover passes **Rp4,8 miliar a year**. Below that, registering is optional.
- Rate: 12%. For goods and services that are not luxury goods, the tax base is
  11/12 of the price, so the effective rate is **11%**. Luxury goods (subject to
  PPnBM) pay the full 12%. Basis: PMK 131/2024 and PMK 11/2025. *check*
- Restaurant food and drink is not subject to PPN; it falls under PBJT (below).

## PBJT food and drink (formerly PB1, the "restaurant tax")

- A regional tax on food and drink sold by restaurants, cafés, catering and
  similar, under UU 1/2022 (HKPD). **Up to 10%**, with the rate and the turnover
  threshold set by each regency or city in its own Perda. *check the region*
- Collected from the customer on top of the price and paid to the regional tax
  office (Bapenda). Small sellers under the regional threshold may not have to
  collect it.
- Delivery apps usually show it separately; confirm how your platform handles it.

## Employees

- **PPh 21**: the employer withholds income tax from wages, using the TER
  monthly rates (PP 58/2023). Payroll apps calculate it.
- **PPh 23** may apply when a business pays a company for certain services, or
  is paid by one. The accountant sets this up.

## What the checker looks for

| item | what is wrong |
| --- | --- |
| PPh Final 0.5% | not paid, or paid on net sales after the apps' cut instead of gross turnover |
| PBJT / PPN collected | counted as sales, or collected from customers and not paid on |
| Turnover near Rp4,8 miliar | the PKP and PPN question is coming and nobody has planned for it |
| Records | no record of turnover per month: the tax office and any bank will ask for it |
