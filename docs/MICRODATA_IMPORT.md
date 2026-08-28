# HCES and ASUSE Manual Import

MoSPI's official download manual requires: open the catalog, choose **Get Microdata**, register or
log in, activate the account through the emailed link, complete the dataset application, accept the
data access agreement, download the RAR and extract the files. This is a genuine user-authentication
blocker and is not bypassed.

Required catalogs:

- HCES 2023-24: `https://microdata.gov.in/NADA/index.php/catalog/237`
- HCES 2022-23: `https://microdata.gov.in/NADA/index.php/catalog/224`
- ASUSE 2023-24: `https://microdata.gov.in/NADA/index.php/catalog/238`

After lawful download, extract/convert only the required levels to CSV, map the exact official
columns in `config/hces_mapping.example.json` or `config/asuse_mapping.example.json`, and run:

```sh
.venv/bin/python scripts/import_hces.py <csv-directory> <mapping.json> <output.json>
.venv/bin/python scripts/import_asuse.py <csv-directory> <mapping.json> <output.json>
```

Each output records every input filename, byte size and checksum. HCES outputs are sampled weighted
per-capita priors; ASUSE outputs are sampled weighted sector priors. Neither is labelled as an exact
locality observation or incumbent-business measurement.
