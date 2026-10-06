# PROJECT STATE
Last updated: 2026-10-06 (Atlas — full working files uploaded)

## Summary
Shared board for a multi-agent collaboration on Jase's physics/cosmology
hypothesis portfolio. Canonical per-hypothesis detail lives in
`hypotheses/<slug>/README.md`; the ranked register is
`hypotheses/REGISTRY.md`. **Working files (code, notes, data) now live in
`hypotheses/<slug>/files/`, indexed by `hypotheses/<slug>/FILES.md`.**
`portfolio-ledger-2026-10-06.md` is the research-control ledger (internal,
not a scientific result).

## Active Tasks
- **Kerr/CS ALMA search (active):** 3 of 8 EBs searched with the repaired
  v2 pipeline (null result, calibrated); 5 EBs still reducing.
  See `hypotheses/kerr-cs-polarimetry/README.md`.
- **Pulsar crypto idea #2 (to confirm):** shared-key generation from
  common single-pulse structure + location-dependent scintillation.
  Feasibility workup proposed, awaiting Jase's go-ahead.
- **PRTP NANOGrav radio pilot (designed, pending Jase's go).**

## Notes
- Repo is the shared cognition layer. `hypotheses/<slug>/files/` now holds
  the actual code, notes, and small data products (254 files, ~7 MB in the
  2026-10-06 upload). Heavy/bulky primary data (ALMA raw tars, NANOGrav
  chains, NICER events, DESI FITS) is NOT mirrored; each `FILES.md` says
  where to fetch it.
- Binary `.npz` files were converted to plain CSV/JSON on upload: several
  connected apps fetch GitHub contents as text and can corrupt binaries.
  Conversions are value-identical (spot-checked row counts and checksums).
- Claims discipline (standing rule): never label anything validated,
  production-ready, falsified, or detected without reproducible
  calculations, stated assumptions, proper statistics, and independent
  validation. Other agents' reports are hypotheses until checked.
- Public repo: no credentials, personal data, or private identifiers.
  Staged tree secret-scanned 2026-10-06 (no hits).
