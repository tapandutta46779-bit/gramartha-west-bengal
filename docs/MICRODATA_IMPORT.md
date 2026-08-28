# HCES and ASUSE Restricted-Microdata Import

The authorized MoSPI applications and data-access agreements have been completed. The original CSV
ZIP archives are retained unchanged in `work/raw_stage/*_RESTRICTED_MICRODATA/`; the importers stream
only required CSV members and do not create duplicate extracted copies.

Required catalogs:

- HCES 2023-24: `https://microdata.gov.in/NADA/index.php/catalog/237`
- HCES 2022-23: `https://microdata.gov.in/NADA/index.php/catalog/224`
- ASUSE 2023-24: `https://microdata.gov.in/NADA/index.php/catalog/238`

Run the checksum-recording transforms directly against the archives:

```sh
.venv/bin/python scripts/import_hces.py work/raw_stage/HCES_2023_24_RESTRICTED_MICRODATA/HCES_Data_2023-24_Csv.zip config/hces_2023_24_mapping.json outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/HCES_2023_24_West_Bengal_liquid_milk_priors.json
.venv/bin/python scripts/import_hces.py work/raw_stage/HCES_2022_23_RESTRICTED_MICRODATA/CSV_data_HH_Cons_exp_22_23.zip config/hces_2022_23_mapping.json outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/HCES_2022_23_West_Bengal_liquid_milk_priors.json
.venv/bin/python scripts/import_asuse.py work/raw_stage/ASUSE_2023_24_RESTRICTED_MICRODATA/ASUSE_DATA_2023_24_CSV.zip config/asuse_2023_24_mapping.json outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/ASUSE_2023_24_West_Bengal_enterprise_priors.json
```

HCES keeps zero-consumption households in the denominator and emits person-weighted monthly
per-capita priors. ASUSE uses the publisher's `MLT / 100` final weight, official items 765/766/769
for input/output/GVA, item 789 for workers, the published asset categories, and the official annual
reference-period conversion. Its district names come from Appendix II of the ASUSE 2023-24 field
instructions.

The 95% ranges are labelled normal approximations from weighted household/enterprise variation;
they are not complex-survey design standard errors. Every result remains a sampled district/sector
prior, never an exact locality observation or incumbent-business measurement.

The raw archives are applicant-only under the MoSPI agreement. They may be backed up privately for
the applicant, but must not be placed in the public share package or redistributed. Aggregate outputs,
code, checksums, methodology and provenance may be shared.
