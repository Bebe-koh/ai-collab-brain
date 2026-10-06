# Provenance — GRB catalog rebuild attempt (2026-09-24)

## What was built
`grb_catalog_greiner.csv` — 2,965 rows parsed from Jochen Greiner's public GRB
compilation table.

- Source URL: https://www.mpe.mpg.de/~jcg/grbgen.html
- Accessed/downloaded: 2026-09-24 (~15:26 PDT) via HTTPS.
- Parser: `~/workspace/grb/parse_greiner.py` (regex over `<TR VALIGN="TOP">` rows).
- Columns: `name, ra_deg, dec_deg, z_raw, z, z_flag`
  - `z_raw`: verbatim redshift cell (preserves qualifiers like `1.95ul`, `<2.2`, `1.068h`).
  - `z`: numeric value or empty.
  - `z_flag`: `clean` (bare number), `none` (empty), or `qualified:<raw>`.

## Counts vs the recorded original
| metric | recorded original | this rebuild |
|---|---|---|
| total rows | 9,180 | **2,965** |
| with redshift entry | (not recorded) | 768 |
| z in [1.6, 2.1] | 82 | **99** (includes qualified/photo-z/limit entries) |

## Verdict
**This is NOT the original 9,180-row catalog.** Greiner's table contains only
bursts localized to <1° (~3,000 entries) and cannot produce 9,180 rows.
No other public single-source catalog matches 9,180 rows either
(Swift GRB table ~1,700; Fermi GBM ~3,500; BATSE 2,704).

## Best hypothesis for the original
The IceCube **GRBweb** database (https://user-web.icecube.wisc.edu/~grbweb_public/)
aggregates Swift + Fermi GBM + IPN + BATSE + BeppoSAX + others into one
deduplicated table and is the most plausible source of a ~9,180-row
all-instrument catalog. Its front page advertises bulk data
("Accessible as SQLite or txt file"), but the download links are not exposed
in the page text and the "Get Started" summary-table page failed to load on
2026-09-24, so the bulk catalog could not be retrieved. The original catalog
file itself is not in the workspace and was not found in any public location.

## What would unblock this
1. Jase locates his original 9,180-row file (check downloads / analysis folders
   from the original HCBGW work), or
2. Retrieve the GRBweb SQLite/txt bulk download (needs a working browser session
   on the GRBweb site), then re-run the count verification.
