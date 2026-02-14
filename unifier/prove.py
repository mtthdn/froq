#!/usr/bin/env python3
"""Prove Python unification is equivalent to CUE lattice unification.

Four proofs:
1. MERGE EQUIVALENCE: Python merge of per-source data == CUE unified output
2. COMMUTATIVITY:     Merge in any source order produces same result
3. IDEMPOTENCY:       Merging same source twice produces same result
4. PROJECTION EQUIVALENCE: Python projections on unified data == CUE projections

Run: python3 unifier/prove.py
"""

import json
import random
import sys
from pathlib import Path

# Add repo root to path so imports work when run as script
repo_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, repo_root)

from unifier.merge import merge_all_sources
from unifier.source_reader import (
    SOURCE_FILES,
    SOURCE_NAMES,
    read_all_sources,
    read_cue_projection,
    read_cue_unified,
)
from unifier.projections import (
    project_anomalies,
    project_enrichment,
    project_funding_gaps,
    project_gap_report,
    project_gene_sources,
    project_weighted_gaps,
)

PASS = "PASS"
FAIL = "FAIL"


def deep_compare(a, b, path=""):
    """Recursively compare two values, returning list of (path, a_val, b_val) diffs."""
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        all_keys = set(a.keys()) | set(b.keys())
        for key in sorted(all_keys):
            child_path = f"{path}.{key}" if path else key
            if key not in a:
                diffs.append((child_path, "<missing>", b[key]))
            elif key not in b:
                diffs.append((child_path, a[key], "<missing>"))
            else:
                diffs.extend(deep_compare(a[key], b[key], child_path))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append((f"{path}[len]", len(a), len(b)))
        for i in range(min(len(a), len(b))):
            diffs.extend(deep_compare(a[i], b[i], f"{path}[{i}]"))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        # Numeric comparison: CUE may export 1 vs 1.0
        if abs(float(a) - float(b)) > 1e-10:
            diffs.append((path, a, b))
    elif a != b:
        diffs.append((path, a, b))
    return diffs


def strip_hidden(gene_dict: dict) -> dict:
    """Remove _in_* fields from a gene dict for comparison with CUE export.

    CUE doesn't export hidden fields in the genes expression --
    we compare those separately via gene_sources.
    """
    return {k: v for k, v in gene_dict.items() if not k.startswith("_")}


def prove_merge_equivalence(cue_unified, python_unified, gene_list):
    """Proof 1: Python merge == CUE unified output, field by field."""
    print("\n=== MERGE EQUIVALENCE PROOF ===")

    total_fields = 0
    matched_fields = 0
    mismatches = []

    for symbol in sorted(gene_list):
        cue_gene = cue_unified.get(symbol, {})
        py_gene = python_unified.get(symbol, {})

        # Compare visible fields (CUE genes export omits _in_* hidden fields)
        cue_visible = strip_hidden(cue_gene)
        py_visible = strip_hidden(py_gene)

        diffs = deep_compare(cue_visible, py_visible, path=symbol)
        field_count = len(cue_visible)
        total_fields += field_count
        matched_fields += field_count - len(diffs)

        for path, cue_val, py_val in diffs:
            mismatches.append((path, cue_val, py_val))

        # Also compare _in_* flags
        for flag in ["_in_go", "_in_omim", "_in_hpo", "_in_uniprot",
                      "_in_facebase", "_in_clinvar", "_in_pubmed",
                      "_in_gnomad", "_in_nih_reporter", "_in_gtex",
                      "_in_clinicaltrials", "_in_string"]:
            total_fields += 1
            cue_val = cue_gene.get(flag, False)
            py_val = py_gene.get(flag, False)
            if cue_val == py_val:
                matched_fields += 1
            else:
                mismatches.append((f"{symbol}.{flag}", cue_val, py_val))

    print(f"  Checked {len(gene_list)} genes, {total_fields} field comparisons")
    print(f"  MATCH: {matched_fields} / {total_fields} ({100*matched_fields//total_fields}%)")

    if mismatches:
        print(f"\n  MISMATCHES ({len(mismatches)}):")
        for path, cue_val, py_val in mismatches[:20]:
            print(f"    {path}: CUE={cue_val!r}  Python={py_val!r}")
        if len(mismatches) > 20:
            print(f"    ... and {len(mismatches) - 20} more")
        return FAIL

    return PASS


def prove_commutativity(gene_list, all_contributions, shuffles=5):
    """Proof 2: Merge in any order produces the same result."""
    print(f"\n=== COMMUTATIVITY PROOF ({shuffles} shuffles) ===")

    # Canonical merge (original order)
    canonical = merge_all_sources(gene_list, all_contributions)

    all_pass = True
    for i in range(shuffles):
        shuffled = list(all_contributions)
        random.shuffle(shuffled)
        result = merge_all_sources(gene_list, shuffled)

        diffs = deep_compare(canonical, result)
        if diffs:
            print(f"  Shuffle {i+1}: FAIL ({len(diffs)} diffs)")
            for path, a, b in diffs[:5]:
                print(f"    {path}: canonical={a!r}  shuffled={b!r}")
            all_pass = False
        else:
            print(f"  Shuffle {i+1}: MATCH (all fields identical)")

    return PASS if all_pass else FAIL


def prove_idempotency(gene_list, all_contributions):
    """Proof 3: Merging any source twice produces the same result."""
    print("\n=== IDEMPOTENCY PROOF ===")

    # Canonical merge
    canonical = merge_all_sources(gene_list, all_contributions)

    all_pass = True
    for idx, source_data in enumerate(all_contributions):
        source_name = list(SOURCE_NAMES.values())[idx]
        # Double the source: merge it once more
        doubled = list(all_contributions) + [source_data]
        result = merge_all_sources(gene_list, doubled)

        diffs = deep_compare(canonical, result)
        if diffs:
            print(f"  Double-merge {source_name}: FAIL ({len(diffs)} diffs)")
            for path, a, b in diffs[:3]:
                print(f"    {path}: single={a!r}  doubled={b!r}")
            all_pass = False
        else:
            print(f"  Double-merge {source_name}: MATCH")

    return PASS if all_pass else FAIL


def prove_projection_equivalence(python_unified):
    """Proof 4: Python projections match CUE projection exports."""
    print("\n=== PROJECTION EQUIVALENCE PROOF ===")

    projections = {
        "gene_sources": (project_gene_sources, "gene_sources"),
        "enrichment": (project_enrichment, "enrichment"),
        "gap_report": (project_gap_report, "gap_report"),
        "funding_gaps": (project_funding_gaps, "funding_gaps"),
        "weighted_gaps": (project_weighted_gaps, "weighted_gaps"),
        "anomalies": (project_anomalies, "anomalies"),
    }

    all_pass = True
    for name, (func, cue_expr) in projections.items():
        print(f"  {name}: ", end="", flush=True)
        cue_data = read_cue_projection(cue_expr, repo_root=repo_root)
        py_data = func(python_unified)

        diffs = deep_compare(cue_data, py_data)
        if diffs:
            print(f"FAIL ({len(diffs)} diffs)")
            for path, cue_val, py_val in diffs[:5]:
                print(f"    {path}: CUE={cue_val!r}  Python={py_val!r}")
            all_pass = False
        else:
            print("MATCH")

    return PASS if all_pass else FAIL


def main():
    print("=" * 60)
    print("PYTHON UNIFICATION EQUIVALENCE PROOF")
    print("=" * 60)

    # Step 1: Read CUE's unified output as ground truth
    print("\nReading CUE unified output (ground truth)...")
    cue_unified = read_cue_unified(repo_root=repo_root)
    gene_list = sorted(cue_unified.keys())
    print(f"  {len(gene_list)} genes in unified model")

    # Step 2: Read each source individually
    print("\nReading 12 source files...")
    all_contributions = read_all_sources(repo_root=repo_root)

    # Step 3: Merge in Python
    print("\nMerging in Python...")
    python_unified = merge_all_sources(gene_list, all_contributions)
    print(f"  Merged {len(python_unified)} genes")

    # Proof 1: Merge equivalence
    results = {}
    results["merge"] = prove_merge_equivalence(
        cue_unified, python_unified, gene_list
    )

    # Proof 2: Commutativity
    results["commutativity"] = prove_commutativity(
        gene_list, all_contributions
    )

    # Proof 3: Idempotency
    results["idempotency"] = prove_idempotency(
        gene_list, all_contributions
    )

    # Proof 4: Projection equivalence
    results["projections"] = prove_projection_equivalence(python_unified)

    # Summary
    print("\n" + "=" * 60)
    all_passed = all(v == PASS for v in results.values())
    for name, result in results.items():
        print(f"  {name}: {result}")
    print("=" * 60)

    if all_passed:
        print("\nPROOF COMPLETE: Python unification is equivalent to CUE.")
        return 0
    else:
        print("\nPROOF FAILED: See mismatches above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
