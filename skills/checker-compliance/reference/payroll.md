# Wages and payroll costs

Checked November 2026. Items marked *check* change yearly. Not legal advice:
confirm with Disnaker, BPJS or a payroll consultant.

## Minimum wage

- Each province sets a **UMP**; many regencies and cities set a higher **UMK**.
  The UMK applies where it exists. New figures are announced late in the year
  and apply from 1 January. *check every year*
- Example, 2026: UMP DKI Jakarta **Rp5.729.876** a month (Kepgub 1142/2025),
  the highest in the country; West Java's UMP is the lowest at Rp2.317.601,
  but its industrial regencies (Bekasi, Karawang) set far higher UMKs.
- Minimum wage applies to workers with under one year of service; longer-serving
  staff should be on a wage scale.
- **Micro and small businesses** may agree wages below the minimum wage with
  their workers, within a floor set by the wage regulation (PP 36/2021 and its
  amendments, most recently PP 49/2025). *check* the current floor with
  Disnaker before relying on it, and say so in the plan.

## BPJS (social security)

Percentages of the monthly wage. *check* the wage caps, which change.

| programme | employer | employee | note |
| --- | ---: | ---: | --- |
| BPJS Kesehatan (health) | 4% | 1% | wage counted up to Rp12.000.000 |
| JKK (work accidents) | 0.24% to 1.74% | | by risk; offices and cafés are at the low end |
| JKM (death) | 0.30% | | |
| JHT (old-age savings) | 3.7% | 2% | |
| JP (pension) | 2% | 1% | wage counted up to a cap revised each year |

For a low-risk business the employer pays roughly **10.24% of wages** (4 + 0.24 +
0.30 + 3.7 + 2). Use that as the estimate and label it as one. JKP
(job-loss insurance) is funded from the other programmes, not a new
contribution. Contributions are due by the 10th of the next month.

## THR (religious holiday allowance)

- Every worker with at least one month of service gets THR once a year, before
  their religious holiday (usually Idul Fitri; Christmas, Nyepi, Waisak or Imlek
  for others).
- 12 months of service or more: **one month's wage**. 1 to 12 months: pro rata,
  months worked / 12 x one month's wage. Basis: Permenaker 6/2016, with a
  circular from the Minister each year.
- Paid **no later than 7 days before the holiday**. In `checker/actuals.json` it sits in labour
  for the month it is paid, usually the month before Lebaran (see calendar.md).

## Hours and overtime

- 40 hours a week: 7 hours x 6 days or 8 hours x 5 days.
- Overtime (PP 35/2021): at most 4 hours a day and 18 hours a week, with the
  worker's agreement. Pay on a working day: 1.5 x the hourly wage for the first
  hour, 2 x after that. Hourly wage = monthly wage / 173. Rest days and public
  holidays pay more.

## Contracts

- **PKWT** (fixed-term contract): at the end, the worker gets compensation of one
  month's wage per 12 months worked, pro rata (PP 35/2021).
- **PKWTT** (permanent): severance rules apply on termination. Budget for it in
  the risk register, not in the monthly costs.
- Daily or casual workers (harian lepas): allowed under limits; still covered by
  BPJS Ketenagakerjaan.

## What the checker looks for

| item | where it shows | what is wrong |
| --- | --- | --- |
| Wages at UMK (or the agreed wage) | labour in `checker/actuals.json` | wages under the UMK with no written agreement under the micro and small business rule |
| Employer BPJS, about 10.24% of wages (estimate) | labour | not registered, or paid on a wage lower than the real one |
| THR | labour, in the month it was paid | not paid, paid late, or paid in goods only |
| Overtime | labour | regular overtime with no extra pay |

## After Lebaran

Many workers go home for mudik and some do not come back. Plan the rota for the
weeks around Lebaran and budget for hiring and training afterwards.
