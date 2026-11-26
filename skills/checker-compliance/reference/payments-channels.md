# How Indonesians pay and buy

Checked November 2026. Platform fees change several times a year: always use the
rate in the seller centre or the merchant contract, and mark anything else as an
estimate.

## Payments

| method | what to know |
| --- | --- |
| **QRIS** | the national QR standard, accepted by every bank app and e-wallet. Merchant fee (MDR) from 1 October 2026: **0% on payments up to Rp100.000 for every merchant**; micro merchants (UMI) also 0% up to Rp500.000 and 0.3% above; small, medium and large merchants 0.7% above Rp100.000. The fee is on the whole payment and may not be passed to the customer. *check* bi.go.id |
| E-wallets | GoPay, OVO, DANA, ShopeePay, LinkAja. Their cashback promos drive where promo hunters buy |
| Bank transfer and virtual accounts | common for online orders and B2B; reconcile daily |
| Debit cards (GPN) | in shops; EDC terminals from banks |
| Credit cards | a minority of buyers; higher fees |
| **COD** (cash on delivery) | still important outside the big cities and for first-time buyers; higher return and failed-delivery rates |
| Paylater | SPayLater, GoPayLater, Kredivo, Akulaku: lifts basket size; the platform takes a fee |
| Payment gateways | Midtrans, Xendit, DOKU and others, for your own website: per-method fees |

## Food delivery apps

- **GoFood, GrabFood, ShopeeFood**. Merchant commission has historically been
  around 20% of the menu price or more, plus optional ads and promo
  co-funding. In 2026 the government cut ride-hailing commissions and is reviewing
  delivery commissions; the outcome for food merchants was not settled when this
  was checked. *check* GoBiz, GrabMerchant, ShopeeFood Partner.
- Many merchants set app prices higher than counter prices to cover the
  commission. Record each channel's gross and commission separately in
  `checker/actuals.json`.
- Payouts arrive a few days after the order. Note the real delay in
  `checker/business.md`: it decides how much cash the business needs on hand.

## Marketplaces and social commerce

- **Shopee**, **Tokopedia and TikTok Shop** (run together under TikTok since
  2024), **Lazada**, **Blibli**.
- Fees stack: an admin or commission fee by category, a payment or transaction
  fee, optional programme fees (free shipping, cashback, extra vouchers),
  affiliate commissions, and ads. They rose repeatedly in 2025 and 2026.
  *check* each seller centre and add them up per order.
- Money is released after the buyer confirms receipt or an automatic period
  passes, so cash lags sales by days to weeks.
- **TikTok live and affiliates**: creators earn a commission per sale; very
  effective for fashion, beauty, snacks and gadgets.

## Direct and social channels

- **WhatsApp Business** (catalogue, broadcast lists, groups): the default way
  small businesses take repeat orders. Follow the data rules (permits.md).
- **Instagram and TikTok**: discovery; most buyers check them before trying a new
  place or brand.
- **Google Business Profile and Google Maps**: essential for anything with a
  location; reviews drive walk-ins.
- **Resellers and dropshippers**: a classic Indonesian distribution model for
  physical products: tiered wholesale prices, a reseller group, content they can
  repost.
- **Communities**: office buildings, campuses, housing complexes (perumahan),
  arisan and religious study groups, hobby groups.

## Logistics

- Parcel: JNE, J&T Express, SiCepat, AnterAja, Ninja Xpress, Pos Indonesia, and
  the platforms' own couriers. Aggregators compare rates.
- Same-day and instant: GoSend, GrabExpress, Lalamove, and similar.
- Outside Java, delivery is slower and dearer: test before promising times.

## Selling to government and big companies

- Government buying for UMK: LKPP e-Katalog and Bela Pengadaan.
- Big companies pay on terms (30 to 90 days) and may withhold PPh 23: model the
  cash gap.
