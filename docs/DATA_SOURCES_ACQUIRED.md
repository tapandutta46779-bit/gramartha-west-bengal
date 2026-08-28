# Data Sources Acquired

| Source | Coverage | Raw status |
|---|---|---|
| DS057 20th Livestock Census village/ward workbook | National raw retained; every available WB row extracted | Verified SHA-256 `8917232...595`; WB extract `c26a01f...2555` |
| Geo2day/OpenStreetMap West Bengal PBF | West Bengal | 113,098,966 bytes; SHA-256 `b5b0c617...6cca`; publisher companion MD5 conflict retained |
| Census 2011 Location Code Directory | National raw required; state code 19 extracted | 23,318,601 bytes; SHA-256 `e5670123...dd0` |
| Census 2011 PCA TV | All 19 WB districts as defined in 2011 | 19/19 XLSX files, individual hashes in manifest |
| HCES 2022-23/2023-24 technical files and CSV unit records | National sample; no WB archive | Acquired under restricted applicant access; CRC and SHA-256 verified; raw records not publicly redistributable |
| ASUSE 2023-24 technical files and CSV unit records | National sample; no WB archive | Acquired under restricted applicant access; 98,219,217 bytes, SHA-256 `82a2e59a...de54` |
| ASUSE calendar-2025 technical files and CSV unit records | National sample; no WB archive | Acquired under restricted applicant access; 173,738,167 bytes, SHA-256 `f20b35ab...591` |
| HCES West Bengal priors | 23 survey district groups / rural-urban sector | 2022-23 comparison and 2023-24 production-safe aggregate priors |
| ASUSE West Bengal priors | 23 survey district groups / rural-urban sector / NIC2 | 2023-24 comparison and calendar-2025 production-safe aggregate priors |
| Fitted survey models | West Bengal district holdout | Private joblib artifacts plus public-safe metrics/registry; ordinary inference uses direct survey priors |

Exact byte sizes, URLs and complete hashes are in the JSON manifests beside the derived outputs.
