# CLAUDE.md — froq

## What This Is
Neural crest gene reconciliation pipeline. Normalizers transform biomedical
database exports (APIs, bulk files) into CUE files. CUE unifies them via
lattice semantics. Generators produce JSON summaries and VizData.

## Commands
- `just validate` — CUE model validation
- `just generate` — Export projections as JSON
- `just vizdata` — Generate VizData for graph explorer
- `just rebuild` — Full pipeline from API data
- `just summary` — Quick coverage stats
- `just check <gene>` — Spot-check a specific gene (e.g., `just check IRF6`)
- `just gaps` — Show research gap report

## Architecture
```
normalizers/ (API/file inputs) -> model/ (CUE unification) -> generators/ (JSON/VizData)
```

## Key Patterns
- Sources OBSERVE, Resolutions DECIDE (no shared mutable fields)
- Per-source ID namespacing: `go_id`, `omim_id`, etc.
- Defaulted booleans for source markers: `_in_go: *false | true`
- Canonical key is HGNC gene symbol
- CUE CONSTRUCTS the reconciled model through lattice unification
- See ADDING-A-SOURCE.md for the plugin pattern

## Key Files
- `model/schema.cue` — #Gene type definition (the contract)
- `normalizers/genes.py` — Shared gene list + HGNC ID lookup table
- `normalizers/from_*.py` — Per-source normalizers
- `generators/to_vizdata.py` — VizData JSON for graph explorer
- `generators/to_summary.py` — Human-readable summary
