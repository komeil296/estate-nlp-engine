# Estate NLP — Divar Weak-Label Agreement

- Database: `divar_ads.sqlite`
- Sample per category: **300**
- Actual sample size: **1,819** (includes all explicit `rent_to_single` labels)
- Database access: read-only
- Raw advertisement text: not printed or saved

> These are agreement measurements against source labels, not gold-standard accuracy. A structured source value may be absent from the text or may not be perfectly reliable.

## Sample size by category

| Category | Sample records |
|---|---:|
| `commercial-rent` | 300 |
| `commercial-sell` | 300 |
| `real-estate-services` | 300 |
| `residential-rent` | 319 |
| `residential-sell` | 300 |
| `temporary-rent` | 300 |

## Overall weak-label agreement

| Field | Labeled | Decided | Abstained | Matches | Mismatches | Coverage | Agreement on decided | Agreement on all |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `allow_single_person` | 19 | 1 | 18 | 1 | 0 | 5.26% | 100.0% | 5.26% |
| `building_area_sqm` | 1,516 | 515 | 1,001 | 445 | 70 | 33.97% | 86.41% | 29.35% |
| `feature.balcony` | 392 | 5 | 387 | 5 | 0 | 1.28% | 100.0% | 1.28% |
| `feature.electricity` | 68 | 2 | 66 | 1 | 1 | 2.94% | 50.0% | 1.47% |
| `feature.elevator` | 524 | 24 | 500 | 24 | 0 | 4.58% | 100.0% | 4.58% |
| `feature.gas` | 68 | 0 | 68 | 0 | 0 | 0.0% | n/a% | 0.0% |
| `feature.jacuzzi` | 58 | 0 | 58 | 0 | 0 | 0.0% | n/a% | 0.0% |
| `feature.parking` | 684 | 42 | 642 | 40 | 2 | 6.14% | 95.24% | 5.85% |
| `feature.pool` | 62 | 0 | 62 | 0 | 0 | 0.0% | n/a% | 0.0% |
| `feature.sauna` | 57 | 0 | 57 | 0 | 0 | 0.0% | n/a% | 0.0% |
| `feature.security_guard` | 60 | 0 | 60 | 0 | 0 | 0.0% | n/a% | 0.0% |
| `feature.warehouse` | 684 | 16 | 668 | 16 | 0 | 2.34% | 100.0% | 2.34% |
| `feature.water` | 69 | 3 | 66 | 0 | 3 | 4.35% | 0.0% | 0.0% |
| `land_area_sqm` | 160 | 33 | 127 | 28 | 5 | 20.62% | 84.85% | 17.5% |
| `property_type` | 1,241 | 668 | 573 | 551 | 117 | 53.83% | 82.49% | 44.4% |
| `rooms` | 1,452 | 403 | 1,049 | 373 | 30 | 27.75% | 92.56% | 25.69% |
| `transaction_type` | 1,819 | 959 | 860 | 679 | 280 | 52.72% | 70.8% | 37.33% |

## Field agreement by category

### `allow_single_person`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 19 | 1 | 1 | 0 | 18 | 5.26% | 100.0% |

### `building_area_sqm`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 297 | 123 | 110 | 13 | 174 | 41.41% | 89.43% |
| `commercial-sell` | 300 | 109 | 92 | 17 | 191 | 36.33% | 84.4% |
| `residential-rent` | 319 | 151 | 137 | 14 | 168 | 47.34% | 90.73% |
| `residential-sell` | 300 | 112 | 97 | 15 | 188 | 37.33% | 86.61% |
| `temporary-rent` | 300 | 20 | 9 | 11 | 280 | 6.67% | 45.0% |

### `feature.balcony`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 216 | 4 | 4 | 0 | 212 | 1.85% | 100.0% |
| `residential-sell` | 176 | 1 | 1 | 0 | 175 | 0.57% | 100.0% |

### `feature.electricity`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 12 | 1 | 1 | 0 | 11 | 8.33% | 100.0% |
| `residential-sell` | 17 | 1 | 0 | 1 | 16 | 5.88% | 0.0% |
| `temporary-rent` | 39 | 0 | 0 | 0 | 39 | 0.0% | n/a% |

### `feature.elevator`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 87 | 3 | 3 | 0 | 84 | 3.45% | 100.0% |
| `commercial-sell` | 37 | 3 | 3 | 0 | 34 | 8.11% | 100.0% |
| `residential-rent` | 232 | 9 | 9 | 0 | 223 | 3.88% | 100.0% |
| `residential-sell` | 168 | 9 | 9 | 0 | 159 | 5.36% | 100.0% |

### `feature.gas`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 12 | 0 | 0 | 0 | 12 | 0.0% | n/a% |
| `residential-sell` | 17 | 0 | 0 | 0 | 17 | 0.0% | n/a% |
| `temporary-rent` | 39 | 0 | 0 | 0 | 39 | 0.0% | n/a% |

### `feature.jacuzzi`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `residential-sell` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `temporary-rent` | 36 | 0 | 0 | 0 | 36 | 0.0% | n/a% |

### `feature.parking`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 87 | 4 | 4 | 0 | 83 | 4.6% | 100.0% |
| `commercial-sell` | 37 | 4 | 4 | 0 | 33 | 10.81% | 100.0% |
| `residential-rent` | 319 | 18 | 17 | 1 | 301 | 5.64% | 94.44% |
| `residential-sell` | 241 | 16 | 15 | 1 | 225 | 6.64% | 93.75% |

### `feature.pool`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `residential-sell` | 14 | 0 | 0 | 0 | 14 | 0.0% | n/a% |
| `temporary-rent` | 37 | 0 | 0 | 0 | 37 | 0.0% | n/a% |

### `feature.sauna`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `residential-sell` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `temporary-rent` | 35 | 0 | 0 | 0 | 35 | 0.0% | n/a% |

### `feature.security_guard`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 11 | 0 | 0 | 0 | 11 | 0.0% | n/a% |
| `residential-sell` | 15 | 0 | 0 | 0 | 15 | 0.0% | n/a% |
| `temporary-rent` | 34 | 0 | 0 | 0 | 34 | 0.0% | n/a% |

### `feature.warehouse`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 87 | 0 | 0 | 0 | 87 | 0.0% | n/a% |
| `commercial-sell` | 37 | 2 | 2 | 0 | 35 | 5.41% | 100.0% |
| `residential-rent` | 319 | 6 | 6 | 0 | 313 | 1.88% | 100.0% |
| `residential-sell` | 241 | 8 | 8 | 0 | 233 | 3.32% | 100.0% |

### `feature.water`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 12 | 0 | 0 | 0 | 12 | 0.0% | n/a% |
| `residential-sell` | 17 | 2 | 0 | 2 | 15 | 11.76% | 0.0% |
| `temporary-rent` | 40 | 1 | 0 | 1 | 39 | 2.5% | 0.0% |

### `land_area_sqm`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `residential-rent` | 87 | 6 | 4 | 2 | 81 | 6.9% | 66.67% |
| `residential-sell` | 73 | 27 | 24 | 3 | 46 | 36.99% | 88.89% |

### `property_type`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 274 | 175 | 155 | 20 | 99 | 63.87% | 88.57% |
| `commercial-sell` | 208 | 141 | 123 | 18 | 67 | 67.79% | 87.23% |
| `residential-rent` | 232 | 113 | 84 | 29 | 119 | 48.71% | 74.34% |
| `residential-sell` | 227 | 124 | 104 | 20 | 103 | 54.63% | 83.87% |
| `temporary-rent` | 300 | 115 | 85 | 30 | 185 | 38.33% | 73.91% |

### `rooms`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 295 | 15 | 13 | 2 | 280 | 5.08% | 86.67% |
| `commercial-sell` | 297 | 12 | 10 | 2 | 285 | 4.04% | 83.33% |
| `residential-rent` | 319 | 165 | 156 | 9 | 154 | 51.72% | 94.55% |
| `residential-sell` | 241 | 123 | 118 | 5 | 118 | 51.04% | 95.93% |
| `temporary-rent` | 300 | 88 | 76 | 12 | 212 | 29.33% | 86.36% |

### `transaction_type`

| Category | Labeled | Decided | Matches | Mismatches | Abstained | Coverage | Agreement on decided |
|---|---:|---:|---:|---:|---:|---:|---:|
| `commercial-rent` | 300 | 135 | 119 | 16 | 165 | 45.0% | 88.15% |
| `commercial-sell` | 300 | 153 | 143 | 10 | 147 | 51.0% | 93.46% |
| `real-estate-services` | 300 | 200 | 133 | 67 | 100 | 66.67% | 66.5% |
| `residential-rent` | 319 | 140 | 123 | 17 | 179 | 43.89% | 87.86% |
| `residential-sell` | 300 | 132 | 112 | 20 | 168 | 44.0% | 84.85% |
| `temporary-rent` | 300 | 199 | 49 | 150 | 101 | 66.33% | 24.62% |

## Interpretation

- Low coverage means the extractor often abstains; it is not automatically a wrong prediction.
- Agreement is not precision/recall because the source labels are weak and may not be expressed in the ad text.
- The `house-villa-*` source classes are intentionally excluded from a single property-type target because they combine two types.
- The complete `rent_to_single` labeled subset is included because the source field has very few labeled rows.
- Do not use this report alone to claim model quality or to train a final model.
