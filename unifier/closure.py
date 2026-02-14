"""Transitive closure on gene relationships.

CUE can compute pairwise relationships (gene A shares phenotype with gene B)
but cannot compute transitive closure at scale (>20 genes causes timeouts).

Python computes full transitive closure trivially using union-find or networkx.

Edge types:
    1. Shared phenotypes: genes sharing HPO phenotype strings
       (only phenotypes shared by 2-5 genes, to filter universal ones)
    2. Shared syndromes: genes sharing OMIM syndrome strings
    3. Shared GO processes: genes sharing GO biological process terms (aspect "P")
       (only terms shared by 2-8 genes, to filter universal ones)
    4. STRING PPI: genes that are STRING interaction partners of each other
"""

from __future__ import annotations

from collections import defaultdict

import networkx as nx


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def _build_inverted_index(
    genes: dict,
    field: str,
    *,
    extract: callable = None,
    min_sharing: int = 2,
    max_sharing: int = 5,
) -> dict[str, set[str]]:
    """Build an inverted index: term -> set of gene symbols that have it.

    Args:
        genes: unified gene dict
        field: field name to pull values from (must be a list)
        extract: optional callable to extract the string key from each
                 list element (e.g., lambda t: t["term_name"])
        min_sharing: minimum number of genes sharing a term to keep it
        max_sharing: maximum number of genes sharing a term to keep it
                     (filters out universal terms)

    Returns:
        {term_string: {symbol, symbol, ...}} filtered by sharing range
    """
    index: dict[str, set[str]] = defaultdict(set)
    for sym, g in genes.items():
        values = g.get(field, [])
        if not values:
            continue
        for item in values:
            key = extract(item) if extract else item
            index[key].add(sym)

    # Filter by sharing range
    return {
        term: syms
        for term, syms in index.items()
        if min_sharing <= len(syms) <= max_sharing
    }


def _add_edges_from_index(
    G: nx.Graph,
    index: dict[str, set[str]],
    edge_type: str,
) -> int:
    """Add edges between all gene pairs that share a term.

    Returns the number of edges added.
    """
    added = 0
    for term, symbols in index.items():
        sym_list = sorted(symbols)
        for i in range(len(sym_list)):
            for j in range(i + 1, len(sym_list)):
                a, b = sym_list[i], sym_list[j]
                if G.has_edge(a, b):
                    # Add this edge type to existing edge
                    G[a][b]["types"].add(edge_type)
                    G[a][b]["shared_terms"].setdefault(edge_type, []).append(term)
                else:
                    G.add_edge(
                        a, b,
                        types={edge_type},
                        shared_terms={edge_type: [term]},
                    )
                    added += 1
    return added


def build_relationship_graph(genes: dict) -> nx.Graph:
    """Build a gene-gene relationship graph from unified data.

    Edge types:
    1. Shared phenotypes: genes that share HPO phenotype strings
       (only phenotypes shared by 2-5 genes, to avoid universal ones)
    2. Shared syndromes: genes that share OMIM syndrome strings
    3. Shared GO processes: genes that share GO biological process terms (aspect "P")
       (only terms shared by 2-8 genes)
    4. STRING PPI: genes that are STRING interaction partners of each other
    """
    G = nx.Graph()

    # Add all genes as nodes
    for sym in genes:
        G.add_node(sym)

    # 1. Shared phenotypes (HPO phenotype strings)
    pheno_index = _build_inverted_index(
        genes, "phenotypes",
        min_sharing=2, max_sharing=5,
    )
    _add_edges_from_index(G, pheno_index, "phenotype")

    # 2. Shared syndromes (OMIM syndrome strings)
    syndrome_index = _build_inverted_index(
        genes, "omim_syndromes",
        min_sharing=2, max_sharing=100,  # syndromes are specific enough
    )
    _add_edges_from_index(G, syndrome_index, "syndrome")

    # 3. Shared GO biological processes (aspect "P" only)
    # Filter GO terms to just biological processes
    go_process_genes: dict[str, set[str]] = defaultdict(set)
    for sym, g in genes.items():
        for term in g.get("go_terms", []):
            if term.get("aspect") == "P":
                go_process_genes[term["term_name"]].add(sym)

    # Filter to terms shared by 2-8 genes
    go_filtered = {
        term: syms
        for term, syms in go_process_genes.items()
        if 2 <= len(syms) <= 8
    }
    _add_edges_from_index(G, go_filtered, "pathway")

    # 4. STRING PPI: genes that list each other as interaction partners
    for sym, g in genes.items():
        partners = g.get("string_partners", [])
        for partner in partners:
            if partner in genes:
                # Only add if both exist in our gene set
                if G.has_edge(sym, partner):
                    G[sym][partner]["types"].add("ppi")
                else:
                    G.add_edge(sym, partner, types={"ppi"}, shared_terms={})

    return G


def build_typed_graph(genes: dict, edge_type: str) -> nx.Graph:
    """Build a graph for a single edge type only.

    Valid edge_type values: "phenotype", "syndrome", "pathway", "ppi"
    """
    G = nx.Graph()
    for sym in genes:
        G.add_node(sym)

    if edge_type == "phenotype":
        idx = _build_inverted_index(
            genes, "phenotypes", min_sharing=2, max_sharing=5,
        )
        _add_edges_from_index(G, idx, "phenotype")

    elif edge_type == "syndrome":
        idx = _build_inverted_index(
            genes, "omim_syndromes", min_sharing=2, max_sharing=100,
        )
        _add_edges_from_index(G, idx, "syndrome")

    elif edge_type == "pathway":
        go_index: dict[str, set[str]] = defaultdict(set)
        for sym, g in genes.items():
            for term in g.get("go_terms", []):
                if term.get("aspect") == "P":
                    go_index[term["term_name"]].add(sym)
        filtered = {t: s for t, s in go_index.items() if 2 <= len(s) <= 8}
        _add_edges_from_index(G, filtered, "pathway")

    elif edge_type == "ppi":
        for sym, g in genes.items():
            for partner in g.get("string_partners", []):
                if partner in genes:
                    if not G.has_edge(sym, partner):
                        G.add_edge(sym, partner, types={"ppi"}, shared_terms={})

    return G


# ---------------------------------------------------------------------------
# Transitive closure
# ---------------------------------------------------------------------------

def transitive_closure(G: nx.Graph) -> list[set[str]]:
    """Compute transitive closure as connected components.

    If A~B and B~C, then {A,B,C} form a component.
    Returns list of gene symbol sets, one per component, sorted by
    descending size then alphabetical first element.
    """
    components = [set(c) for c in nx.connected_components(G)]
    components.sort(key=lambda c: (-len(c), min(c)))
    return components


def closure_by_edge_type(genes: dict) -> dict:
    """Compute transitive closure separately for each relationship type.

    Returns: {
        "phenotype_components": [...sets...],
        "syndrome_components": [...sets...],
        "pathway_components": [...sets...],
        "ppi_components": [...sets...],
        "all_components": [...sets...],  # combined graph
    }
    """
    result = {}
    for etype in ["phenotype", "syndrome", "pathway", "ppi"]:
        G = build_typed_graph(genes, etype)
        components = transitive_closure(G)
        # Only include non-singleton components
        result[f"{etype}_components"] = [c for c in components if len(c) > 1]

    # Combined graph
    G_all = build_relationship_graph(genes)
    all_comps = transitive_closure(G_all)
    result["all_components"] = [c for c in all_comps if len(c) > 1]

    return result


# ---------------------------------------------------------------------------
# Centrality analysis
# ---------------------------------------------------------------------------

def centrality_analysis(G: nx.Graph) -> dict:
    """Compute graph centrality metrics.

    Returns: {
        symbol: {
            "degree": int,
            "betweenness": float,
            "closeness": float,
            "community": int,
        }
    }
    """
    if G.number_of_nodes() == 0:
        return {}

    degree = dict(G.degree())
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    communities = community_detection(G)

    # Build reverse mapping: symbol -> community_id
    sym_to_community = {}
    for cid, members in communities.items():
        for sym in members:
            sym_to_community[sym] = cid

    result = {}
    for sym in G.nodes():
        result[sym] = {
            "degree": degree[sym],
            "betweenness": round(betweenness[sym], 6),
            "closeness": round(closeness[sym], 6),
            "community": sym_to_community.get(sym, -1),
        }

    return result


# ---------------------------------------------------------------------------
# Community detection
# ---------------------------------------------------------------------------

def community_detection(G: nx.Graph) -> dict[int, set[str]]:
    """Detect communities via label propagation.

    Returns: {community_id: set of gene symbols}
    """
    if G.number_of_nodes() == 0:
        return {}

    communities = nx.community.label_propagation_communities(G)
    return {i: set(c) for i, c in enumerate(communities)}


# ---------------------------------------------------------------------------
# Full closure report
# ---------------------------------------------------------------------------

def closure_report(genes: dict) -> dict:
    """Full closure analysis report.

    Returns: {
        "graph_stats": {nodes, edges, components, density},
        "edge_type_counts": {phenotype, syndrome, pathway, ppi},
        "components": [...],
        "hub_genes": [...],
        "bridge_genes": [...],
        "communities": [...],
        "largest_closure": {...},
    }
    """
    G = build_relationship_graph(genes)

    # Graph stats
    num_components = nx.number_connected_components(G)
    density = nx.density(G) if G.number_of_nodes() > 1 else 0.0

    graph_stats = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "components": num_components,
        "density": round(density, 6),
    }

    # Edge type counts: count edges where each type appears
    edge_type_counts = {"phenotype": 0, "syndrome": 0, "pathway": 0, "ppi": 0}
    for u, v, data in G.edges(data=True):
        for etype in data.get("types", set()):
            edge_type_counts[etype] = edge_type_counts.get(etype, 0) + 1

    # Components (non-singleton, sorted by size)
    components = transitive_closure(G)
    component_descriptions = []
    for comp in components:
        if len(comp) < 2:
            continue
        # Find dominant edge types within this component
        subgraph = G.subgraph(comp)
        comp_edge_types: dict[str, int] = defaultdict(int)
        for u, v, data in subgraph.edges(data=True):
            for etype in data.get("types", set()):
                comp_edge_types[etype] += 1

        dominant = max(comp_edge_types, key=comp_edge_types.get) if comp_edge_types else "none"
        component_descriptions.append({
            "genes": sorted(comp),
            "size": len(comp),
            "edges": subgraph.number_of_edges(),
            "dominant_relationship": dominant,
            "edge_breakdown": dict(comp_edge_types),
        })

    # Centrality-based rankings
    centrality = centrality_analysis(G)

    # Hub genes: top 10 by degree centrality
    hub_genes = sorted(
        centrality.items(),
        key=lambda x: (-x[1]["degree"], x[0]),
    )[:10]
    hub_genes = [
        {"symbol": sym, "degree": c["degree"], "betweenness": c["betweenness"]}
        for sym, c in hub_genes
        if c["degree"] > 0
    ]

    # Bridge genes: top 10 by betweenness centrality
    bridge_genes = sorted(
        centrality.items(),
        key=lambda x: (-x[1]["betweenness"], x[0]),
    )[:10]
    bridge_genes = [
        {"symbol": sym, "betweenness": c["betweenness"], "degree": c["degree"]}
        for sym, c in bridge_genes
        if c["betweenness"] > 0
    ]

    # Communities
    communities = community_detection(G)
    community_descriptions = []
    for cid, members in sorted(communities.items()):
        if len(members) < 2:
            continue
        community_descriptions.append({
            "community_id": cid,
            "genes": sorted(members),
            "size": len(members),
        })

    # Largest closure
    largest = max(components, key=len) if components else set()
    largest_subgraph = G.subgraph(largest) if largest else nx.Graph()
    largest_edge_types: dict[str, int] = defaultdict(int)
    for u, v, data in largest_subgraph.edges(data=True):
        for etype in data.get("types", set()):
            largest_edge_types[etype] += 1
    dominant_role = max(largest_edge_types, key=largest_edge_types.get) if largest_edge_types else "none"

    largest_closure = {
        "genes": sorted(largest),
        "size": len(largest),
        "dominant_role": dominant_role,
    }

    return {
        "graph_stats": graph_stats,
        "edge_type_counts": edge_type_counts,
        "components": component_descriptions,
        "hub_genes": hub_genes,
        "bridge_genes": bridge_genes,
        "communities": community_descriptions,
        "largest_closure": largest_closure,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import subprocess
    import sys

    # Load unified genes from CUE
    print("Loading unified genes from CUE...", file=sys.stderr)
    proc = subprocess.run(
        ["cue", "export", "./model/", "-e", "genes"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(f"cue export failed: {proc.stderr}", file=sys.stderr)
        sys.exit(1)
    genes_data = json.loads(proc.stdout)

    # Also load source flags
    proc2 = subprocess.run(
        ["cue", "export", "./model/", "-e", "gene_sources"],
        capture_output=True, text=True,
    )
    if proc2.returncode != 0:
        print(f"cue export gene_sources failed: {proc2.stderr}", file=sys.stderr)
        sys.exit(1)
    source_flags = json.loads(proc2.stdout)

    # Merge _in_* flags into gene dicts
    for symbol, flags in source_flags.items():
        if symbol in genes_data:
            for flag_name, flag_value in flags.items():
                genes_data[symbol][f"_{flag_name}"] = flag_value

    print(f"Loaded {len(genes_data)} genes", file=sys.stderr)

    # Build graph and compute closure
    print("Building relationship graph...", file=sys.stderr)
    G = build_relationship_graph(genes_data)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges",
          file=sys.stderr)

    # Compute transitive closure
    print("Computing transitive closure...", file=sys.stderr)
    components = transitive_closure(G)
    non_singleton = [c for c in components if len(c) > 1]
    print(f"Found {len(non_singleton)} non-singleton components", file=sys.stderr)

    # Full report
    print("Generating closure report...", file=sys.stderr)
    report = closure_report(genes_data)
    print(json.dumps(report, indent=2, default=list))
