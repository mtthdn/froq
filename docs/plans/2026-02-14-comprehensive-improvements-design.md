# Comprehensive Improvements Design

**Date:** 2026-02-14
**Status:** Approved

## Overview

20 improvements across 5 workstreams: infrastructure hardening, 3 new data
sources, schema enhancements, analytics, and site improvements.

## Workstream 1: Infrastructure & Pipeline Hardening

1. `requirements.txt` — declare `requests`, `jinja2`
2. Pin CUE version — `.cue-version` + justfile check
3. Structured error reporting — `PipelineReport` in `normalizers/pipeline.py`
4. Staleness-aware refresh — `just refresh --stale-days N`
5. Integration test — 5-gene subset (SOX9, IRF6, PAX3, RET, MITF)
6. Parallel fetching — `concurrent.futures` in `just normalize-parallel`

## Workstream 2: New Data Sources

7. gnomAD (`from_gnomad.py`) — constraint scores via GraphQL API
8. NIH Reporter (`from_nih_reporter.py`) — active grants via REST v2
9. GTEx (`from_gtex.py`) — tissue expression via Portal API

All follow existing pattern: cache in `data/`, write to `model/`, own fields.

## Workstream 3: Schema & Model

10. Gene list as CUE — `model/gene_list.cue` alongside `genes.py`
11. Clean hidden/exported field separation
12. Weighted gap scoring — `proj_weighted_gaps.cue`
13. Update gap/funding projections for 10 sources

## Workstream 4: VizData & Analytics

14. GO pathway cluster edges in vizdata
15. Publication trend analysis (velocity, direction)
16. Pre-loaded NIDCR portfolio comparison

## Workstream 5: Site Improvements

17. Jinja2 template extraction from `to_site.py`
18. Temporal diffing (snapshot comparison)
19. Mobile responsiveness (CSS media queries)
20. Accessibility (ARIA, keyboard nav, skip-link)

## Decisions

- Jinja2 for templates (lightweight, Python-native)
- gnomAD GraphQL (gene-specific queries)
- NIH Reporter REST v2 (public, no auth)
- GTEx Portal API (public)
- 5-gene test subset for integration test
- Skip OMIM live API (no key available)
