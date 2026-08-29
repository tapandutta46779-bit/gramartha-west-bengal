# West Bengal Current Geography Audit

Canonical layer: `CURRENT_PRODUCT_GEOGRAPHY_V1`.

The customer-facing layer contains exactly 23 current product districts. Original source geography remains unchanged. Census-2011 entities are stored separately and crosswalked only when hierarchy-compatible.

| District | Blocks | Municipalities | Towns | Villages | Wards | Coordinates | Census crosswalks | Priors | Search | Analysis |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Alipurduar | 6 | 1 | 0 | 354 | 20 | 20 | 346 | 46 | PASS | CONDITIONAL |
| Bankura | 22 | 3 | 0 | 3464 | 58 | 38 | 157 | 46 | PASS | CONDITIONAL |
| Birbhum | 19 | 6 | 0 | 2251 | 99 | 400 | 29 | 46 | PASS | CONDITIONAL |
| Cooch Behar | 12 | 6 | 0 | 1142 | 77 | 11 | 8 | 46 | PASS | CONDITIONAL |
| Dakshin Dinajpur | 8 | 3 | 0 | 1545 | 54 | 18 | 13 | 44 | PASS | CONDITIONAL |
| Darjeeling | 9 | 5 | 0 | 537 | 118 | 6 | 2 | 46 | PASS | CONDITIONAL |
| Hooghly | 18 | 13 | 0 | 1907 | 300 | 24 | 0 | 46 | PASS | CONDITIONAL |
| Howrah | 14 | 2 | 0 | 779 | 98 | 13 | 0 | 46 | PASS | CONDITIONAL |
| Jalpaiguri | 7 | 3 | 0 | 408 | 57 | 71 | 1 | 46 | PASS | CONDITIONAL |
| Jhargram | 8 | 1 | 0 | 2363 | 17 | 13 | 2600 | 44 | PASS | CONDITIONAL |
| Kalimpong | 3 | 1 | 0 | 104 | 21 | 0 | 104 | 36 | PASS | CONDITIONAL |
| Kolkata | 0 | 1 | 0 | 0 | 142 | 0 | 0 | 24 | PASS | CONDITIONAL |
| Malda | 15 | 2 | 0 | 1634 | 42 | 36 | 16 | 46 | PASS | CONDITIONAL |
| Murshidabad | 26 | 8 | 0 | 1932 | 145 | 28 | 28 | 46 | PASS | CONDITIONAL |
| Nadia | 17 | 11 | 0 | 1270 | 201 | 47 | 16 | 46 | PASS | CONDITIONAL |
| North 24 Parganas | 22 | 27 | 0 | 1571 | 665 | 34 | 3 | 46 | PASS | CONDITIONAL |
| Paschim Bardhaman | 8 | 2 | 0 | 384 | 92 | 8 | 384 | 46 | PASS | CONDITIONAL |
| Paschim Medinipur | 21 | 8 | 0 | 4908 | 119 | 15 | 471 | 46 | PASS | CONDITIONAL |
| Purba Bardhaman | 23 | 11 | 0 | 2120 | 207 | 87 | 2129 | 46 | PASS | CONDITIONAL |
| Purba Medinipur | 25 | 5 | 0 | 2907 | 99 | 18 | 73 | 46 | PASS | CONDITIONAL |
| Purulia | 20 | 3 | 0 | 2433 | 48 | 26 | 104 | 46 | PASS | CONDITIONAL |
| South 24 Parganas | 29 | 7 | 0 | 2082 | 148 | 1966 | 17 | 46 | PASS | CONDITIONAL |
| Uttar Dinajpur | 9 | 4 | 0 | 1476 | 76 | 182 | 5 | 46 | PASS | CONDITIONAL |

## Hierarchy checks

- `orphan_nodes`: 0
- `wrong_parent_district`: 0
- `same_parent_duplicates`: 0
- `cross_district_source_leakage`: 0

## Limitations

- LGD bulk download is CAPTCHA-gated and was not acquired in this run.
- DS057 publisher labels define the provisional current product hierarchy.
- Historical Census observations retain year 2011 after crosswalk.
- Exact locality crosswalks require compatible current hierarchy; unsafe split-era matches remain unmapped.
