# Estate NLP — Divar Financial Weak-Label Evaluation

- Database: `divar_ads.sqlite`
- Sample per category: **300**
- Seed: **20261030**
- Actual sample size: **1,800**
- Database access: read-only
- Raw advertisement text/evidence: not printed or saved
- Source currency/unit: unspecified; no currency conversion applied

> Source numeric columns are weak labels, not gold annotations. An amount may not be repeated in the text. Exact amount matches are reported separately from role matches. Possible scale factors are diagnostic only and are not counted as correct.

## Sample size by category

| Category | Sample records |
|---|---:|
| `commercial-rent` | 300 |
| `commercial-sell` | 300 |
| `real-estate-services` | 300 |
| `residential-rent` | 300 |
| `residential-sell` | 300 |
| `temporary-rent` | 300 |

## Financial field results

| Category | Source field | Expected role | Positive labels | Zero labels | NULL labels | Exact role + value | Exact value, wrong role | Role, wrong value | No financial mention | Other mentions only | Possible scale factor |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | `credit_value` | `deposit` | 292 | 6 | 2 | 3 | 2 | 3 | 258 | 26 | 0 |
| `commercial-rent` | `rent_value` | `monthly_rent` | 275 | 23 | 2 | 2 | 0 | 13 | 241 | 19 | 3 |
| `commercial-sell` | `price_value` | `asking_price` | 243 | 1 | 56 | 1 | 0 | 6 | 217 | 19 | 0 |
| `residential-rent` | `credit_value` | `deposit` | 299 | 1 | 0 | 4 | 2 | 14 | 253 | 26 | 5 |
| `residential-rent` | `rent_value` | `monthly_rent` | 238 | 60 | 2 | 1 | 1 | 14 | 202 | 20 | 3 |
| `residential-sell` | `price_value` | `asking_price` | 288 | 1 | 11 | 2 | 0 | 8 | 245 | 33 | 0 |
| `temporary-rent` | `cost_per_extra_person` | `cost_per_extra_person` | 116 | 5 | 179 | 1 | 2 | 3 | 98 | 12 | 1 |
| `temporary-rent` | `rent_price_at_weekends` | `weekend_rent` | 143 | 3 | 154 | 0 | 1 | 0 | 124 | 18 | 0 |
| `temporary-rent` | `rent_price_on_regular_days` | `daily_rent` | 195 | 3 | 102 | 1 | 1 | 5 | 172 | 16 | 0 |
| `temporary-rent` | `rent_price_on_special_days` | `special_day_rent` | 120 | 2 | 178 | 0 | 1 | 0 | 106 | 13 | 0 |

## Source mode distribution in sampled records

| Category | Mode field | Value | Count |
|---|---|---|---:|
| `commercial-rent` | `credit_mode` | `توافقی` | 2 |
| `commercial-rent` | `credit_mode` | `مجانی` | 6 |
| `commercial-rent` | `credit_mode` | `مقطوع` | 292 |
| `commercial-rent` | `rent_mode` | `توافقی` | 2 |
| `commercial-rent` | `rent_mode` | `مجانی` | 23 |
| `commercial-rent` | `rent_mode` | `مقطوع` | 275 |
| `commercial-sell` | `price_mode` | `(NULL)` | 49 |
| `commercial-sell` | `price_mode` | `توافقی` | 7 |
| `commercial-sell` | `price_mode` | `مجانی` | 1 |
| `commercial-sell` | `price_mode` | `مقطوع` | 243 |
| `residential-rent` | `credit_mode` | `مجانی` | 1 |
| `residential-rent` | `credit_mode` | `مقطوع` | 299 |
| `residential-rent` | `rent_mode` | `توافقی` | 2 |
| `residential-rent` | `rent_mode` | `مجانی` | 60 |
| `residential-rent` | `rent_mode` | `مقطوع` | 238 |
| `residential-sell` | `price_mode` | `(NULL)` | 10 |
| `residential-sell` | `price_mode` | `توافقی` | 1 |
| `residential-sell` | `price_mode` | `مجانی` | 1 |
| `residential-sell` | `price_mode` | `مقطوع` | 288 |

## Diagnostic mismatches (IDs and numbers only; no ad text)

### `commercial-rent.credit_value`

- source_row=417810; expected=20000000.0; predicted=deposit:2; kind=role found, amount differs
- source_row=577855; expected=300000000.0; predicted=deposit:200000000; kind=role found, amount differs
- source_row=752875; expected=20000000.0; predicted=monthly_rent:20000000; kind=exact amount, role differs

### `commercial-rent.rent_value`

- source_row=64090; expected=25000000.0; predicted=monthly_rent:2, monthly_rent:20, monthly_rent:30, monthly_rent:6; kind=role found, amount differs
- source_row=157549; expected=50000000.0; predicted=monthly_rent:6; kind=role found, amount differs
- source_row=165356; expected=4500000.0; predicted=monthly_rent:4, monthly_rent:3; kind=role found, amount differs

### `commercial-sell.price_value`

- source_row=195605; expected=2100000000.0; predicted=asking_price:200000000; kind=role found, amount differs
- source_row=371680; expected=46000000000.0; predicted=asking_price:3; kind=role found, amount differs
- source_row=643853; expected=32500000000.0; predicted=asking_price:35; kind=role found, amount differs

### `residential-rent.credit_value`

- source_row=160208; expected=50000000.0; predicted=unknown:50000000; kind=exact amount, role differs
- source_row=211691; expected=150000000.0; predicted=deposit:150; kind=role found, amount differs
- source_row=225599; expected=280000000.0; predicted=deposit:20; kind=role found, amount differs

### `residential-rent.rent_value`

- source_row=148233; expected=3000000.0; predicted=monthly_rent:185; kind=role found, amount differs
- source_row=153547; expected=100000.0; predicted=monthly_rent:450; kind=role found, amount differs
- source_row=160208; expected=5000000.0; predicted=unknown:5000000; kind=exact amount, role differs

### `residential-sell.price_value`

- source_row=70300; expected=4500000000.0; predicted=asking_price:500000000; kind=role found, amount differs
- source_row=371745; expected=4100000000.0; predicted=asking_price:4300, asking_price:3600, asking_price:3800, asking_price:3800; kind=role found, amount differs
- source_row=389614; expected=1500000000.0; predicted=asking_price:2; kind=role found, amount differs

### `temporary-rent.cost_per_extra_person`

- source_row=155646; expected=50.0; predicted=cost_per_extra_person:4, cost_per_extra_person:50000; kind=role found, amount differs
- source_row=639629; expected=150000.0; predicted=unknown:150000; kind=exact amount, role differs
- source_row=990097; expected=50000.0; predicted=cost_per_extra_person:0; kind=role found, amount differs

### `temporary-rent.rent_price_at_weekends`

- source_row=646928; expected=350000.0; predicted=unknown:350000; kind=exact amount, role differs

### `temporary-rent.rent_price_on_regular_days`

- source_row=130306; expected=309.0; predicted=daily_rent:300000; kind=role found, amount differs
- source_row=137484; expected=1200000.0; predicted=daily_rent:11; kind=role found, amount differs
- source_row=358310; expected=400.0; predicted=daily_rent:500000; kind=role found, amount differs

### `temporary-rent.rent_price_on_special_days`

- source_row=646928; expected=350000.0; predicted=unknown:350000; kind=exact amount, role differs


## Interpretation and limitations

- `Exact role + value` is the strictest agreement category; it is not gold-standard accuracy.
- `Exact value, wrong role` suggests the amount was seen but its financial meaning was misclassified.
- `Role, wrong value` suggests a role cue was found but a different nearby amount was selected.
- `No financial mention` means the extractor emitted no financial mentions for that sampled ad.
- `Other mentions only` means it emitted financial mentions but none matched this source field/role/value.
- A possible scale factor can indicate a unit or scale mismatch; it must be reviewed, never silently converted.
- The current schema distinguishes `special_day_rent` from `weekend_rent`; the evaluator checks them separately.
- Zero and NULL source amounts are reported separately and are not evaluated as positive text amounts.
