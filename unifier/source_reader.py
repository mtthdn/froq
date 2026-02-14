"""Read per-source data by running CUE on individual source files.

For each of the 12 source files, extracts only the non-default fields
that the source actually contributes. This isolates each source's
contribution so Python can re-merge them identically to CUE.
"""

import json
import subprocess
import sys
from pathlib import Path

from .schema import GENE_DEFAULTS, OPTIONAL_FIELDS, SOURCE_FLAGS

# All 12 source CUE files
SOURCE_FILES = [
    "model/go.cue",
    "model/omim.cue",
    "model/hpo.cue",
    "model/uniprot.cue",
    "model/facebase.cue",
    "model/clinvar.cue",
    "model/pubmed.cue",
    "model/gnomad.cue",
    "model/nih_reporter.cue",
    "model/gtex.cue",
    "model/clinicaltrials.cue",
    "model/string.cue",
]

# Friendly names derived from filenames
SOURCE_NAMES = {
    "model/go.cue": "GO",
    "model/omim.cue": "OMIM",
    "model/hpo.cue": "HPO",
    "model/uniprot.cue": "UniProt",
    "model/facebase.cue": "FaceBase",
    "model/clinvar.cue": "ClinVar",
    "model/pubmed.cue": "PubMed",
    "model/gnomad.cue": "gnomAD",
    "model/nih_reporter.cue": "NIH Reporter",
    "model/gtex.cue": "GTEx",
    "model/clinicaltrials.cue": "ClinicalTrials",
    "model/string.cue": "STRING",
}


def cue_export(expression: str, files: list[str], cwd: str | None = None) -> dict:
    """Run cue export and return parsed JSON.

    Args:
        expression: CUE expression to export (e.g. 'genes')
        files: list of CUE files to load
        cwd: working directory for subprocess
    """
    cmd = ["cue", "export"] + files + ["-e", expression]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"cue export failed: {result.stderr}\nCommand: {' '.join(cmd)}"
        )
    return json.loads(result.stdout)


def read_source(source_file: str, repo_root: str | None = None) -> dict:
    """Export a single source's full gene struct via CUE.

    Runs: cue export model/schema.cue model/gene_list.cue model/<source>.cue -e genes
    plus the proj_sources.cue for hidden _in_* flags.

    Returns the full genes dict (all genes, all fields including defaults).
    """
    files = [
        "model/schema.cue",
        "model/gene_list.cue",
        source_file,
        "model/proj_sources.cue",
    ]
    # Get the visible fields (genes export doesn't include _in_* hidden fields)
    genes_data = cue_export("genes", files[:3], cwd=repo_root)
    # Get the source flags via the projection
    source_flags = cue_export("gene_sources", files, cwd=repo_root)

    # Merge the _in_* flags back into the gene dicts (with underscore prefix)
    for symbol, flags in source_flags.items():
        if symbol in genes_data:
            for flag_name, flag_value in flags.items():
                # proj_sources uses "in_go" etc. -- we need "_in_go"
                hidden_name = f"_{flag_name}"
                genes_data[symbol][hidden_name] = flag_value

    return genes_data


def extract_contributions(full_genes: dict) -> dict:
    """Extract non-default field values from a single-source CUE export.

    Given the full gene struct from a single source (all genes present,
    most fields at defaults), returns only the genes and fields where
    the source actually contributed data.

    Returns: {symbol: {field: value, ...}} only for genes with contributions.
    """
    contributions = {}
    for symbol, gene in full_genes.items():
        non_default = {}
        for field, value in gene.items():
            if field == "symbol":
                continue

            if field in GENE_DEFAULTS:
                # Defaulted field -- skip if at default
                if value == GENE_DEFAULTS[field]:
                    continue
                non_default[field] = value
            else:
                # Optional or unknown field -- always a contribution
                non_default[field] = value

        if non_default:
            contributions[symbol] = non_default

    return contributions


def read_all_sources(repo_root: str | None = None) -> list[dict]:
    """Read all 12 source files and extract their contributions.

    Returns: list of 12 dicts, each is {symbol: {field: value}} for
             genes where that source contributes non-default data.
    """
    all_contributions = []
    for source_file in SOURCE_FILES:
        name = SOURCE_NAMES[source_file]
        full_genes = read_source(source_file, repo_root=repo_root)
        contributions = extract_contributions(full_genes)
        all_contributions.append(contributions)
        print(f"  {name}: {len(contributions)} genes with contributions")
    return all_contributions


def read_cue_unified(repo_root: str | None = None) -> dict:
    """Export CUE's fully unified genes as ground truth.

    Returns the full genes dict with all sources merged by CUE.
    Also includes _in_* flags from the source projection.
    """
    # Get the main genes export
    genes_data = cue_export("genes", ["./model/"], cwd=repo_root)

    # Get the hidden source flags
    source_flags = cue_export("gene_sources", ["./model/"], cwd=repo_root)

    # Merge _in_* flags back in
    for symbol, flags in source_flags.items():
        if symbol in genes_data:
            for flag_name, flag_value in flags.items():
                hidden_name = f"_{flag_name}"
                genes_data[symbol][hidden_name] = flag_value

    return genes_data


def read_cue_projection(expression: str, repo_root: str | None = None) -> dict:
    """Export a CUE projection expression as ground truth."""
    return cue_export(expression, ["./model/"], cwd=repo_root)
