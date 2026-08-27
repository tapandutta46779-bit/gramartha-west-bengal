# SIH26091 share package index

Updated: 2026-08-27

Share root: [SIH26091 Kolkata North 24 Parganas South Bengal Share Package](https://drive.google.com/drive/folders/1MmKbt3u2iQBkgcEbYFrULYpW3ACvyrOU)

The package is organized into raw authoritative files, curated/derived files, manifests, and a
quarantine area. A catalogue entry or URL is not counted as an acquired dataset.

## Verified regional files

| Asset | Exact bytes | SHA-256 / verification | Drive object |
|---|---:|---|---|
| DS057 regional livestock XLSX | 755765 | `3fb48f43fe4b3a500371e46471af8f3da8a2736b07578a0d3e21731c04cc5142` | [File](https://drive.google.com/file/d/1yPvARTw2ZC1-iYBPN5t6mDrxoyrtH5AK/view) |
| Regional evidence SQLite | 57344000 | `fab8ae185c19b55108eb3f31f0f1ae953c77a3f7ad7b66d573e24cfb115ab727`; Drive size read back | [File](https://drive.google.com/file/d/1rnkKaw6JQA0und_UauBZ4vEetCZo8_Sl/view) |
| DS071 West Bengal PBF original | 113098966 | `b5b0c617e22d828954d8754c24aeb5b6440b483260bf040ef9cbbcdfd0e46cca` | Stored losslessly as the two parts below |
| DS071 part aa | 94371840 | `ef83f730b7547c9c36caa5bdaecf307eb531736b31d9367b683be869eaec29d1`; Drive size read back | [File](https://drive.google.com/file/d/1P2uS2cbUGT3qXK8IhvtTfKnRGLX4XwKb/view) |
| DS071 part ab | 18727126 | `a797aa4d08baa90787685b8f7f16714f07f3b09c9df54747cfe186139f7b2175`; Drive size read back | [File](https://drive.google.com/file/d/1skW7-EWWRiEnzkHJfq9zXD31PBXZSuGz/view) |
| DS071 reassembly manifest | 1183 | Drive size read back | [File](https://drive.google.com/file/d/1pFogLPV8m7n7YIn7RGcBYOWG4CLJIhg9/view) |
| DS071 verification record | 1062 | Records the publisher MD5 conflict | [File](https://drive.google.com/file/d/1O76MjJ1UJ93zb7qSQFGtbu8jt3ZPN-zN/view) |
| DS071 polygon boundary | 11979 | Drive size read back | [File](https://drive.google.com/file/d/1mpfsBwpQvHcICaKjMoe1NqZhOa9JVR70/view) |
| DS071 publisher MD5 companion | 97 | Retained as conflicting publisher evidence | [File](https://drive.google.com/file/d/1LIugV305YIGQBgQZCAE30I61Yi1xJEuc/view) |
| Implementation source ZIP | 125282 | `2ad439b2860ec6b41cccddf41db4ff07dd55733ce92565faa2f958361aec9b3e`; Drive size read back | [File](https://drive.google.com/file/d/1tZnE67XnC5bzqOPZDH_JUPfGtOXB_FpJ/view) |
| Five-page implementation/data PDF | 10782 | `9a85614d2cad8ec1572ecd4d3ac77ed94c12216d8710f7015332a715c816346d`; visually checked; Drive size read back | [File](https://drive.google.com/file/d/1saAq90FFonXe9uhB8kEI3q5qv4Ots9ak/view) |

The two West Bengal MSME PDFs and their source manifest are retained in Drive folder
`1wnXfh_3P91RtJQyltXFv8Po1ekOSjk_A`.

Implementation source is committed locally at Git commit `c33bf20`.

## Evidence database content

- 18,326 DS057 source rows processed.
- 9,163 unique dataset-scoped village/ward identities.
- 45,815 observed livestock evidence records.
- Generated DS057 identifiers are explicitly not represented as official LGD or Census codes.
- Male/female counts are summed per species while the sex breakdown remains in record attributes.

## Important limitations

- The DS071 publisher companion MD5 does not match the current HTTP object. The HTTP content
  length and two full-download hashes agree, so the object is retained with a conflict flag rather
  than described as publisher-checksum verified.
- HCES and ASUSE microdata are not acquired.
- A complete official West Bengal LGD/Census crosswalk is not ingested.
- Demand, prices, incumbents, route costs, real venture costs, and current finance rules are not
  sufficiently complete for a real venture recommendation.
- The system therefore returns `INSUFFICIENT_EVIDENCE` instead of fabricating a business answer.
- Public-link visibility of the root folder is not verified. Google Drive returned "sharing is
  unavailable at this time" when the sharing dialog was opened; no permission change was made.
