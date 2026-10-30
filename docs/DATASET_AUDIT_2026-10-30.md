# Divar SQLite — Structural Audit

- Database file: `divar_ads.sqlite`
- Total records: **1,000,000**
- Column count: **61**
- SQLite integrity check: **ok**
- Access mode: read-only
- Raw advertisement text is not included in this report.

## Main categories

| cat2_slug | Records | Share |
|---|---:|---:|
| `residential-sell` | 558,708 | 55.87% |
| `residential-rent` | 276,558 | 27.66% |
| `commercial-rent` | 76,567 | 7.66% |
| `commercial-sell` | 38,861 | 3.89% |
| `temporary-rent` | 29,903 | 2.99% |
| `real-estate-services` | 19,403 | 1.94% |

## Subcategories

| cat2_slug | cat3_slug | Records |
|---|---|---:|
| `commercial-rent` | `shop-rent` | 45,993 |
| `commercial-rent` | `office-rent` | 21,418 |
| `commercial-rent` | `industry-agriculture-business-rent` | 9,155 |
| `commercial-rent` | `(NULL)` | 1 |
| `commercial-sell` | `shop-sell` | 21,855 |
| `commercial-sell` | `industry-agriculture-business-sell` | 11,851 |
| `commercial-sell` | `office-sell` | 5,155 |
| `real-estate-services` | `presell` | 15,781 |
| `real-estate-services` | `partnership` | 3,622 |
| `residential-rent` | `apartment-rent` | 211,880 |
| `residential-rent` | `house-villa-rent` | 64,678 |
| `residential-sell` | `apartment-sell` | 303,385 |
| `residential-sell` | `plot-old` | 133,570 |
| `residential-sell` | `house-villa-sell` | 121,753 |
| `temporary-rent` | `suite-apartment` | 16,465 |
| `temporary-rent` | `villa` | 12,899 |
| `temporary-rent` | `workspace` | 539 |

## Field coverage

| Field | Non-NULL | NULL | Distinct non-NULL |
|---|---:|---:|---:|
| `source_row` | 1,000,000 | 0 | not calculated |
| `cat2_slug` | 1,000,000 | 0 | 6 |
| `cat3_slug` | 999,999 | 1 | 16 |
| `city_slug` | 999,998 | 2 | not calculated |
| `neighborhood_slug` | 437,139 | 562,861 | not calculated |
| `created_at_month` | 1,000,000 | 0 | 46 |
| `user_type` | 288,882 | 711,118 | 2 |
| `title` | 999,946 | 54 | not calculated (free text) |
| `description` | 999,999 | 1 | not calculated (free text) |
| `rent_mode` | 352,994 | 647,006 | 3 |
| `rent_type` | 103,961 | 896,039 | 2 |
| `price_mode` | 573,606 | 426,394 | 3 |
| `credit_mode` | 352,994 | 647,006 | 3 |
| `deed_type` | 253,458 | 746,542 | 5 |
| `rooms_count` | 845,899 | 154,101 | 6 |
| `has_warm_water_provider` | 379,500 | 620,500 | 4 |
| `has_heating_system` | 368,969 | 631,031 | 8 |
| `has_cooling_system` | 350,619 | 649,381 | 6 |
| `has_restroom` | 406,913 | 593,087 | 4 |
| `building_direction` | 323,923 | 676,077 | 5 |
| `floor_material` | 405,984 | 594,016 | 8 |
| `property_type` | 27,057 | 972,943 | 5 |
| `extra_person_capacity` | 24,009 | 975,991 | 31 |
| `floor` | 541,748 | 458,252 | 33 |
| `total_floors_count` | 304,352 | 695,648 | 31 |
| `construction_year` | 815,828 | 184,172 | 34 |
| `rent_value` | 351,322 | 648,678 | not calculated |
| `price_value` | 568,346 | 431,654 | not calculated |
| `credit_value` | 352,095 | 647,905 | not calculated |
| `land_size` | 186,396 | 813,604 | not calculated |
| `building_size` | 980,394 | 19,606 | not calculated |
| `transformable_credit` | 352,085 | 647,915 | not calculated |
| `transformable_rent` | 351,248 | 648,752 | not calculated |
| `transformed_credit` | 72,409 | 927,591 | not calculated |
| `transformed_rent` | 72,409 | 927,591 | not calculated |
| `cost_per_extra_person` | 10,241 | 989,759 | not calculated |
| `rent_price_on_regular_days` | 18,068 | 981,932 | not calculated |
| `rent_price_on_special_days` | 10,463 | 989,537 | not calculated |
| `rent_price_at_weekends` | 13,551 | 986,449 | not calculated |
| `regular_person_capacity` | 29,870 | 970,130 | not calculated |
| `location_latitude` | 655,608 | 344,392 | not calculated |
| `location_longitude` | 655,608 | 344,392 | not calculated |
| `location_radius` | 339,699 | 660,301 | not calculated |
| `unit_per_floor` | 299,954 | 700,046 | not calculated |
| `rent_to_single` | 19 | 999,981 | not calculated |
| `rent_credit_transform` | 352,985 | 647,015 | not calculated |
| `transformable_price` | 352,894 | 647,106 | not calculated |
| `has_business_deed` | 34,679 | 965,321 | not calculated |
| `has_balcony` | 506,188 | 493,812 | not calculated |
| `has_elevator` | 541,749 | 458,251 | not calculated |
| `has_warehouse` | 728,155 | 271,845 | not calculated |
| `has_parking` | 728,156 | 271,844 | not calculated |
| `is_rebuilt` | 529,470 | 470,530 | not calculated |
| `has_water` | 33,444 | 966,556 | not calculated |
| `has_electricity` | 33,445 | 966,555 | not calculated |
| `has_gas` | 33,430 | 966,570 | not calculated |
| `has_security_guard` | 31,312 | 968,688 | not calculated |
| `has_barbecue` | 31,198 | 968,802 | not calculated |
| `has_pool` | 29,390 | 970,610 | not calculated |
| `has_jacuzzi` | 28,728 | 971,272 | not calculated |
| `has_sauna` | 28,479 | 971,521 | not calculated |

## Categorical value distributions

### `cat2_slug`

| Value | Count |
|---|---:|
| `residential-sell` | 558,708 |
| `residential-rent` | 276,558 |
| `commercial-rent` | 76,567 |
| `commercial-sell` | 38,861 |
| `temporary-rent` | 29,903 |
| `real-estate-services` | 19,403 |

### `cat3_slug`

| Value | Count |
|---|---:|
| `apartment-sell` | 303,385 |
| `apartment-rent` | 211,880 |
| `plot-old` | 133,570 |
| `house-villa-sell` | 121,753 |
| `house-villa-rent` | 64,678 |
| `shop-rent` | 45,993 |
| `shop-sell` | 21,855 |
| `office-rent` | 21,418 |
| `suite-apartment` | 16,465 |
| `presell` | 15,781 |
| `villa` | 12,899 |
| `industry-agriculture-business-sell` | 11,851 |
| `industry-agriculture-business-rent` | 9,155 |
| `office-sell` | 5,155 |
| `partnership` | 3,622 |
| `workspace` | 539 |

### `created_at_month`

| Value | Count |
|---|---:|
| `2024-07-01 00:00:00` | 133,219 |
| `2024-08-01 00:00:00` | 132,396 |
| `2024-10-01 00:00:00` | 126,387 |
| `2024-06-01 00:00:00` | 125,624 |
| `2024-11-01 00:00:00` | 121,456 |
| `2024-09-01 00:00:00` | 121,432 |
| `2024-12-01 00:00:00` | 116,452 |
| `2024-05-01 00:00:00` | 108,759 |
| `2024-04-01 00:00:00` | 7,187 |
| `2024-03-01 00:00:00` | 1,881 |
| `2024-02-01 00:00:00` | 1,211 |
| `2025-01-01 00:00:00` | 1,139 |
| `2024-01-01 00:00:00` | 942 |
| `2023-12-01 00:00:00` | 532 |
| `2023-11-01 00:00:00` | 353 |
| `2023-10-01 00:00:00` | 213 |
| `2023-09-01 00:00:00` | 177 |
| `2025-02-01 00:00:00` | 148 |
| `2023-08-01 00:00:00` | 117 |
| `2023-07-01 00:00:00` | 96 |
| `2023-06-01 00:00:00` | 66 |
| `2023-05-01 00:00:00` | 53 |
| `2023-03-01 00:00:00` | 25 |
| `2023-04-01 00:00:00` | 23 |
| `2023-01-01 00:00:00` | 17 |
| `2023-02-01 00:00:00` | 17 |
| `2022-12-01 00:00:00` | 11 |
| `2022-08-01 00:00:00` | 9 |
| `2022-11-01 00:00:00` | 9 |
| `2022-05-01 00:00:00` | 7 |
| `2022-09-01 00:00:00` | 6 |
| `2022-10-01 00:00:00` | 6 |
| `2022-04-01 00:00:00` | 5 |
| `2025-03-01 00:00:00` | 5 |
| `2022-06-01 00:00:00` | 4 |
| `2022-07-01 00:00:00` | 4 |
| `2021-12-01 00:00:00` | 2 |
| `2022-02-01 00:00:00` | 2 |
| `2020-02-01 00:00:00` | 1 |
| `2020-12-01 00:00:00` | 1 |

### `user_type`

| Value | Count |
|---|---:|
| `مشاور املاک` | 256,006 |
| `شخصی` | 32,876 |

### `rent_mode`

| Value | Count |
|---|---:|
| `مقطوع` | 292,081 |
| `مجانی` | 59,241 |
| `توافقی` | 1,672 |

### `rent_type`

| Value | Count |
|---|---:|
| `rent_credit` | 103,814 |
| `full_credit` | 147 |

### `price_mode`

| Value | Count |
|---|---:|
| `مقطوع` | 566,444 |
| `توافقی` | 5,260 |
| `مجانی` | 1,902 |

### `credit_mode`

| Value | Count |
|---|---:|
| `مقطوع` | 349,231 |
| `مجانی` | 2,864 |
| `توافقی` | 899 |

### `deed_type`

| Value | Count |
|---|---:|
| `single_page` | 194,262 |
| `written_agreement` | 31,873 |
| `other` | 20,288 |
| `multi_page` | 6,466 |
| `unselect` | 569 |

### `rooms_count`

| Value | Count |
|---|---:|
| `دو` | 404,050 |
| `یک` | 192,083 |
| `سه` | 138,633 |
| `بدون اتاق` | 75,898 |
| `چهار` | 21,371 |
| `پنج یا بیشتر` | 13,864 |

### `has_warm_water_provider`

| Value | Count |
|---|---:|
| `package` | 205,641 |
| `water_heater` | 141,082 |
| `powerhouse` | 31,395 |
| `unselect` | 1,382 |

### `has_heating_system`

| Value | Count |
|---|---:|
| `shoofaj` | 201,356 |
| `heater` | 119,771 |
| `duct_split` | 22,047 |
| `floor_heating` | 7,717 |
| `split` | 5,845 |
| `fan_coil` | 5,065 |
| `fireplace` | 4,050 |
| `unselect` | 3,118 |

### `has_cooling_system`

| Value | Count |
|---|---:|
| `water_cooler` | 219,266 |
| `air_conditioner` | 52,341 |
| `split` | 38,708 |
| `duct_split` | 29,373 |
| `unselect` | 5,917 |
| `fan_coil` | 5,014 |

### `has_restroom`

| Value | Count |
|---|---:|
| `squat_seat` | 219,393 |
| `squat` | 179,437 |
| `seat` | 7,455 |
| `unselect` | 628 |

### `building_direction`

| Value | Count |
|---|---:|
| `south` | 159,453 |
| `north` | 142,009 |
| `east` | 12,111 |
| `west` | 7,143 |
| `unselect` | 3,207 |

### `floor_material`

| Value | Count |
|---|---:|
| `ceramic` | 307,821 |
| `stone` | 38,395 |
| `carpet` | 17,696 |
| `mosaic` | 14,611 |
| `wood_parquet` | 14,419 |
| `laminate_parquet` | 9,582 |
| `floor_covering` | 1,793 |
| `unselect` | 1,667 |

### `property_type`

| Value | Count |
|---|---:|
| `jungle` | 16,614 |
| `beach` | 3,990 |
| `other` | 3,832 |
| `jungle-mountain` | 2,399 |
| `mountain` | 222 |

### `extra_person_capacity`

| Value | Count |
|---|---:|
| `2` | 6,852 |
| `1` | 3,911 |
| `4` | 2,846 |
| `3` | 2,086 |
| `5` | 2,066 |
| `6` | 1,166 |
| `10` | 1,066 |
| `0` | 923 |
| `30+` | 724 |
| `8` | 617 |
| `7` | 429 |
| `20` | 304 |
| `15` | 262 |
| `12` | 208 |
| `9` | 104 |
| `25` | 78 |
| `14` | 61 |
| `11` | 52 |
| `16` | 41 |
| `29` | 38 |
| `24` | 32 |
| `13` | 31 |
| `18` | 23 |
| `23` | 14 |
| `22` | 14 |
| `17` | 13 |
| `28` | 12 |
| `26` | 12 |
| `27` | 9 |
| `19` | 9 |
| `21` | 6 |

### `floor`

| Value | Count |
|---|---:|
| `2` | 128,518 |
| `1` | 119,565 |
| `3` | 109,324 |
| `4` | 71,927 |
| `5` | 37,604 |
| `0` | 35,855 |
| `6` | 13,784 |
| `7` | 5,713 |
| `-1` | 4,464 |
| `8` | 3,298 |
| `10` | 2,302 |
| `9` | 2,193 |
| `11` | 1,474 |
| `12` | 1,232 |
| `13` | 834 |
| `14` | 783 |
| `30+` | 675 |
| `15` | 450 |
| `16` | 313 |
| `17` | 269 |
| `20` | 214 |
| `18` | 189 |
| `19` | 153 |
| `21` | 115 |
| `25` | 102 |
| `22` | 87 |
| `23` | 76 |
| `30` | 62 |
| `24` | 61 |
| `27` | 35 |
| `28` | 32 |
| `26` | 25 |
| `29` | 20 |

### `total_floors_count`

| Value | Count |
|---|---:|
| `4` | 89,581 |
| `5` | 79,951 |
| `3` | 52,795 |
| `6` | 28,893 |
| `2` | 22,747 |
| `7` | 8,276 |
| `8` | 4,588 |
| `14` | 3,048 |
| `10` | 2,917 |
| `9` | 2,005 |
| `12` | 1,783 |
| `11` | 1,401 |
| `13` | 1,066 |
| `15` | 993 |
| `16` | 715 |
| `20` | 621 |
| `18` | 455 |
| `25` | 432 |
| `21` | 323 |
| `19` | 311 |
| `17` | 263 |
| `30+` | 233 |
| `30` | 208 |
| `24` | 167 |
| `29` | 148 |
| `22` | 137 |
| `unselect` | 125 |
| `26` | 60 |
| `23` | 42 |
| `27` | 40 |
| `28` | 28 |

### `construction_year`

| Value | Count |
|---|---:|
| `۱۴۰۳` | 116,260 |
| `۱۳۹۰` | 59,139 |
| `۱۴۰۲` | 58,424 |
| `۱۴۰۰` | 53,674 |
| `۱۳۹۵` | 53,029 |
| `۱۳۹۸` | 38,207 |
| `۱۳۹۷` | 36,326 |
| `۱۳۹۶` | 35,487 |
| `۱۴۰۱` | 35,328 |
| `۱۳۸۵` | 34,065 |
| `۱۳۹۹` | 29,594 |
| `۱۳۹۳` | 29,094 |
| `۱۳۹۲` | 26,130 |
| `۱۳۹۴` | 26,110 |
| `۱۳۸۸` | 24,268 |
| `۱۳۸۰` | 23,480 |
| `قبل از ۱۳۷۰` | 20,637 |
| `۱۳۸۹` | 16,755 |
| `۱۳۹۱` | 16,316 |
| `۱۳۸۷` | 14,136 |
| `۱۳۸۶` | 13,468 |
| `۱۳۸۳` | 9,894 |
| `۱۳۸۴` | 8,494 |
| `۱۳۷۵` | 7,247 |
| `۱۳۸۲` | 6,965 |
| `۱۳۷۱` | 5,531 |
| `۱۳۸۱` | 3,590 |
| `۱۳۷۸` | 3,025 |
| `۱۳۷۹` | 2,415 |
| `۱۳۷۷` | 2,117 |
| `۱۳۷۲` | 1,914 |
| `۱۳۷۳` | 1,827 |
| `۱۳۷۶` | 1,593 |
| `۱۳۷۴` | 1,289 |

## Numeric field ranges

| Field | Non-NULL | Zero | Minimum | Maximum |
|---|---:|---:|---:|---:|
| `price_value` | 568,346 | 1,902 | 0.0 | 99999999999999.0 |
| `rent_value` | 351,322 | 59,241 | 0.0 | 999999999999999.0 |
| `credit_value` | 352,095 | 2,864 | 0.0 | 999999999999999.0 |
| `building_size` | 980,394 | 0 | 1.0 | 10000000.0 |
| `land_size` | 186,396 | 0 | 1.0 | 10000000.0 |
| `rent_price_on_regular_days` | 18,068 | 207 | 0.0 | 500600700800900.0 |
| `rent_price_on_special_days` | 10,463 | 241 | 0.0 | 111111111111111.0 |
| `rent_price_at_weekends` | 13,551 | 228 | 0.0 | 200250300400450.0 |
| `cost_per_extra_person` | 10,241 | 473 | 0.0 | 111111111111111.0 |

## Coordinates

- Both coordinates present: **655,608**
- Both coordinates missing: **344,392**
- Only one coordinate present: **0**

## Text-length and Unicode profile

| Field | Non-empty | Average length | Maximum length |
|---|---:|---:|---:|
| `title` | 999,946 | 30.6 | 59 |
| `description` | 999,999 | 273.6 | 1,000 |

Unicode feature scan: **skipped** (pass `--scan-unicode` to enable the slower full-text scan).

## Interpretation notes

- NULL means missing/unknown; it is not equivalent to `false` or zero.
- Categorical heating, cooling, restroom, and hot-water fields must not be flattened to booleans.
- `30+`, `unselect`, and Persian year ranges must retain their raw forms until a range-aware parser is designed.
- Structured financial values are source labels; currency and unit must not be inferred from the column name.
- Source category labels are weak supervision, not a gold-standard annotation.

Audit completed without changing the database.


## Additional verified findings

### Full-text Unicode scan

A separate full scan of all titles and descriptions found these record counts (a record can contain more than one feature):

| Unicode feature | Records |
|---|---:|
| Persian digits | 696,226 |
| Arabic-Indic digits | 6,457 |
| ZWNJ half-space | 168,940 |
| Arabic diacritics | 29,853 |
| Tatweel | 18,004 |
| Bidirectional controls | 7,246 |

The default audit command skips this slower scan. Run with `--scan-unicode` to reproduce it.

### Financial mode distribution

| Field | مقطوع | مجانی | توافقی |
|---|---:|---:|---:|
| `rent_mode` | 292,081 | 59,241 | 1,672 |
| `price_mode` | 566,444 | 1,902 | 5,260 |
| `credit_mode` | 349,231 | 2,864 | 899 |

### Sparse single-person label

- `rent_to_single=1`: 18
- `rent_to_single=0`: 1
- NULL: 999,981

### Suspicious numeric-pattern counts

These are heuristic flags, not proof of invalid data:

| Field | Repeated digit | Repeated block | Increasing chunks | Decreasing chunks |
|---|---:|---:|---:|---:|
| `price_value` | 2,508 | 8 | 13 | 3 |
| `rent_value` | 380 | 0 | 0 | 0 |
| `credit_value` | 431 | 0 | 0 | 0 |
| `cost_per_extra_person` | 7 | 0 | 2 | 0 |
| `rent_price_on_regular_days` | 14 | 0 | 21 | 0 |
| `rent_price_on_special_days` | 9 | 0 | 1 | 0 |
| `rent_price_at_weekends` | 13 | 0 | 6 | 0 |

Do not delete these rows automatically. Preserve them and attach quality flags for review.
