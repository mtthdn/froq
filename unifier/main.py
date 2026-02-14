"""lacuene Python unifier -- equivalent to CUE lattice unification + closure.

Usage:
    python3 -m unifier.main                  # Full run: project + closure
    python3 -m unifier.main --projections    # Only compute projections from CUE data
    python3 -m unifier.main --closure        # Only compute closure from CUE data

All modes load the unified gene data from CUE (cue export ./model/ -e genes),
merge in the hidden _in_* source flags from gene_sources, then compute the
requested outputs.

Output goes to stdout as JSON, with progress messages on stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .source_reader import read_cue_unified
from .projections import compute_all, ALL_PROJECTIONS
from .closure import closure_report, closure_by_edge_type, build_relationship_graph


def load_unified(repo_root: str | None = None) -> dict:
    """Load unified gene data from CUE with source flags merged in."""
    print("Loading unified genes from CUE...", file=sys.stderr)
    unified = read_cue_unified(repo_root=repo_root)
    print(f"  {len(unified)} genes loaded", file=sys.stderr)
    return unified


def run_projections(unified: dict, output_dir: Path | None = None) -> dict:
    """Compute all 6 projections and optionally write to output directory.

    Returns: {projection_name: result_dict}
    """
    print("Computing projections...", file=sys.stderr)
    results = compute_all(unified)

    for name, result in results.items():
        # Quick summary on stderr
        if name == "gene_sources":
            print(f"  gene_sources: {len(result)} genes", file=sys.stderr)
        elif name == "gap_report":
            s = result["summary"]
            print(f"  gap_report: {s['total']} genes, "
                  f"{s['in_all_five']} in all 5, "
                  f"{s['missing_facebase_count']} missing FaceBase",
                  file=sys.stderr)
        elif name == "enrichment":
            print(f"  enrichment: {len(result['tiers'])} genes", file=sys.stderr)
        elif name == "funding_gaps":
            s = result["summary"]
            print(f"  funding_gaps: {s['critical_count']} critical gaps",
                  file=sys.stderr)
        elif name == "weighted_gaps":
            top = sorted(result.items(),
                         key=lambda x: -x[1]["priority_score"])[:3]
            top_names = ", ".join(f"{k}({v['priority_score']})" for k, v in top)
            print(f"  weighted_gaps: top 3 = {top_names}", file=sys.stderr)
        elif name == "anomalies":
            s = result["summary"]
            print(f"  anomalies: {s['total_anomalies']} total", file=sys.stderr)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, result in results.items():
            path = output_dir / f"{name}.json"
            with open(path, "w") as f:
                json.dump(result, f, indent=2)
                f.write("\n")
            print(f"  wrote {path}", file=sys.stderr)

    return results


def run_closure(unified: dict, output_dir: Path | None = None) -> dict:
    """Compute transitive closure and graph analysis.

    Returns the full closure report dict.
    """
    print("Computing transitive closure...", file=sys.stderr)
    report = closure_report(unified)

    stats = report["graph_stats"]
    print(f"  graph: {stats['nodes']} nodes, {stats['edges']} edges, "
          f"{stats['components']} components", file=sys.stderr)
    print(f"  density: {stats['density']}", file=sys.stderr)

    edge_counts = report["edge_type_counts"]
    print(f"  edges by type: {edge_counts}", file=sys.stderr)

    n_comps = len(report["components"])
    print(f"  non-singleton components: {n_comps}", file=sys.stderr)

    lc = report["largest_closure"]
    print(f"  largest closure: {lc['size']} genes, "
          f"dominant role = {lc['dominant_role']}", file=sys.stderr)

    if report["hub_genes"]:
        top_hub = report["hub_genes"][0]
        print(f"  top hub: {top_hub['symbol']} (degree {top_hub['degree']})",
              file=sys.stderr)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "closure_report.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=list)
            f.write("\n")
        print(f"  wrote {path}", file=sys.stderr)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="lacuene Python unifier -- CUE projections + transitive closure",
    )
    parser.add_argument(
        "--projections", action="store_true",
        help="Only compute projections from CUE data",
    )
    parser.add_argument(
        "--closure", action="store_true",
        help="Only compute transitive closure from CUE data",
    )
    parser.add_argument(
        "--output-dir", "-o", type=Path, default=None,
        help="Write output files to this directory (default: stdout)",
    )
    parser.add_argument(
        "--repo-root", type=str, default=None,
        help="Repository root directory (default: current directory)",
    )
    args = parser.parse_args()

    # If neither flag is set, run both
    run_proj = args.projections or (not args.projections and not args.closure)
    run_clos = args.closure or (not args.projections and not args.closure)

    unified = load_unified(repo_root=args.repo_root)

    output = {}

    if run_proj:
        proj_results = run_projections(unified, output_dir=args.output_dir)
        output["projections"] = proj_results

    if run_clos:
        closure_result = run_closure(unified, output_dir=args.output_dir)
        output["closure"] = closure_result

    # Output to stdout if no output directory specified
    if not args.output_dir:
        print(json.dumps(output, indent=2, default=list))


if __name__ == "__main__":
    main()
