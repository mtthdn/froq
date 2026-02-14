# froq — Neural Crest Gene Reconciliation

Reconciles 20 neural crest development genes across 5 public biomedical databases
using CUE's lattice unification. Each source contributes its own fields; CUE unifies
them into a single model and computes gap reports, enrichment tiers, and source
provenance automatically.

## Quick Start

```bash
just rebuild    # full pipeline: normalize → validate → generate
just summary    # coverage stats
just gaps       # research gap report
just vizdata    # Cytoscape.js graph
just report     # human-readable report
just check SOX9 # spot-check a gene
```

## The 20 Genes

Selected to span the full neural crest → craniofacial developmental pipeline:

| Role | Genes |
|------|-------|
| Border specification | PAX3, PAX7, ZIC1, MSX1, MSX2 |
| NC specifiers | SOX9, SOX10, FOXD3, TFAP2A, SNAI1, SNAI2, TWIST1 |
| Patterning / disease | IRF6, TCOF1, CHD7, FGFR2, TBX1, EVC, RUNX2, SHH |

All have known craniofacial phenotypes. All are actively studied at NIDCR.

## 5 Sources

| Source | API | Fields |
|--------|-----|--------|
| Gene Ontology | QuickGO REST | GO terms (MF, BP, CC) |
| OMIM | Bundled genemap2 subset | Disease title, syndromes, inheritance |
| HPO | Bulk annotation file | Clinical phenotype terms |
| UniProt | REST API | Protein name, function, localization, length |
| FaceBase | DERIVA REST | Craniofacial datasets, species, assay type |

## Architecture

```
normalizers/     API queries / file parsing
    from_go.py ─────────┐
    from_omim.py ────────┤
    from_hpo.py ─────────┤
    from_uniprot.py ─────┤  each writes one CUE file
    from_facebase.py ────┘
                         ↓
model/           CUE lattice unification
    schema.cue ─── #Gene type definition
    go.cue ──────┐
    omim.cue ────┤
    hpo.cue ─────┤  unify into `genes` struct
    uniprot.cue ─┤
    facebase.cue ┘
    proj_*.cue ──── computed projections (gap report, enrichment, provenance)
                         ↓
generators/      JSON / graph output
    to_summary.py ── human-readable coverage report
    to_vizdata.py ── Cytoscape.js graph (shared phenotypes/syndromes)
```

## Key Pattern: Sources OBSERVE, Resolutions DECIDE

Each source owns its fields exclusively:
- `go.cue` sets `_in_go: true`, `go_id`, `go_terms`
- `omim.cue` sets `_in_omim: true`, `omim_id`, `omim_syndromes`
- No source touches another source's fields

Projections compute derived views (gap reports, enrichment) from the unified model.

## Example Output

```
20 genes unified across 5 sources

Coverage:
  5 sources:   9 genes
  4 sources:  10 genes
  3 sources:   1 gene

Research Gaps (OMIM disease but no FaceBase data): 11
  CHD7      CHARGE syndrome, 214800
  TCOF1     Treacher Collins syndrome 1, 154500
  SOX10     Waardenburg syndrome, type 4C, 613266
  ...
```

## Adding a Source

See [ADDING-A-SOURCE.md](ADDING-A-SOURCE.md).
