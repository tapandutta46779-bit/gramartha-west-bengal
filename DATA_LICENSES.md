# Data and third-party licensing

The repository contains several legal categories of material. The top-level MIT `LICENSE` applies to **original GramArtha source code**. It does not override the terms of third-party data, documents or assets.

## OpenStreetMap-derived material

GramArtha contains OSM-derived spatial extracts and public-runtime material.

- Source: OpenStreetMap contributors
- Database license: Open Database License (ODbL) 1.0
- Attribution: © OpenStreetMap contributors
- Reference: https://www.openstreetmap.org/copyright

Downstream users are responsible for preserving the attribution and complying with the ODbL when redistributing OSM-derived databases or qualifying derivative databases.

## Noto fonts

The PDF reporting layer bundles Noto Bengali and Devanagari fonts under `backend/reporting/fonts/`.

The corresponding SIL Open Font License texts are included alongside the font files:

- `OFL-NotoSansBengali.txt`
- `OFL-NotoSansDevanagari.txt`
- `OFL-NotoSerifBengali.txt`

Those fonts remain licensed under their respective SIL Open Font License terms; they are not relicensed under the GramArtha MIT license.

## HCES and ASUSE material

The repository documents processing of HCES and ASUSE survey material. Restricted respondent-level microdata and private fitted model artifacts are intentionally **not distributed in the public deployment runtime**.

Any access to or use of source microdata remains subject to the terms imposed by the original publisher/provider. Derived aggregates, mappings and documentation in this repository do not grant access rights to restricted source microdata.

## Census, livestock and other official-source material

Official publications, statistical tables and government-source documents retain the terms, attribution requirements and reuse conditions of their respective publishers. Their inclusion, transformation or citation by GramArtha does not place them under the project's MIT license.

Where a publisher-specific license is not explicitly recorded in the repository, users should verify the current publisher terms before redistribution.

## Public runtime databases

Files under `deploy/assets/` are compressed, public-safe runtime databases assembled from data that the project is able to distribute in that form. They deliberately exclude restricted respondent microdata and private fitted model artifacts.

A public runtime database can still contain OSM-derived material or other source-specific content; applicable source attribution and licensing obligations therefore continue to apply.

## Project-generated outputs

Purely project-generated source code, schemas and documentation are covered by the top-level MIT license unless a file states otherwise. Generated analytical outputs can embed or summarize third-party evidence; redistribution of those outputs must respect any applicable source terms.

## Adding new data

Every new dataset contribution should document:

1. publisher/source;
2. source URL or stable identifier;
3. acquisition date;
4. observation/effective date;
5. license or terms-of-use status;
6. whether redistribution is permitted;
7. checksum/manifest when practical;
8. freshness classification used by GramArtha.

If redistribution rights are unclear, do not commit the raw dataset to the public repository.
