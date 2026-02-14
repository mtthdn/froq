"""Gene schema -- Python equivalent of model/schema.cue #Gene type.

Mirrors the CUE lattice type definitions so Python can perform
identical unification without calling cue export.
"""

# Default values for each field (mirrors CUE *default | type patterns)
GENE_DEFAULTS = {
    # Per-source IDs (default empty string)
    "go_id": "",
    "omim_id": "",
    "hpo_gene_id": "",
    "uniprot_id": "",
    "facebase_id": "",
    "clinvar_gene_id": "",
    "pubmed_gene_id": "",
    "gnomad_id": "",
    "gtex_id": "",
    "string_id": "",
    # Source presence markers (default False)
    "_in_go": False,
    "_in_omim": False,
    "_in_hpo": False,
    "_in_uniprot": False,
    "_in_facebase": False,
    "_in_clinvar": False,
    "_in_pubmed": False,
    "_in_gnomad": False,
    "_in_nih_reporter": False,
    "_in_gtex": False,
    "_in_clinicaltrials": False,
    "_in_string": False,
}

# Fields that are optional (may or may not be present)
# In CUE these are marked with ? -- absent is valid
OPTIONAL_FIELDS = {
    "go_terms", "omim_title", "omim_syndromes", "inheritance",
    "phenotypes", "protein_name", "organism", "sequence_length",
    "subcellular_locations", "functions", "facebase_datasets",
    "pathogenic_count", "clinvar_variants", "pubmed_total",
    "pubmed_recent", "pubmed_papers", "pli_score", "loeuf_score",
    "oe_lof", "active_grant_count", "nih_reporter_projects",
    "top_tissues", "craniofacial_expression", "active_trial_count",
    "clinicaltrials_studies", "string_interaction_count", "string_partners",
}

SOURCE_FLAGS = [k for k in GENE_DEFAULTS if k.startswith("_in_")]

# Expected types for optional fields (for validation)
OPTIONAL_FIELD_TYPES = {
    "go_terms": list,
    "omim_title": str,
    "omim_syndromes": list,
    "inheritance": str,
    "phenotypes": list,
    "protein_name": str,
    "organism": str,
    "sequence_length": int,
    "subcellular_locations": list,
    "functions": list,
    "facebase_datasets": list,
    "pathogenic_count": int,
    "clinvar_variants": list,
    "pubmed_total": int,
    "pubmed_recent": int,
    "pubmed_papers": list,
    "pli_score": (int, float),
    "loeuf_score": (int, float),
    "oe_lof": (int, float),
    "active_grant_count": int,
    "nih_reporter_projects": list,
    "top_tissues": list,
    "craniofacial_expression": (int, float),
    "active_trial_count": int,
    "clinicaltrials_studies": list,
    "string_interaction_count": int,
    "string_partners": list,
}


def new_gene(symbol: str) -> dict:
    """Return a gene dict with all defaults + symbol set."""
    gene = {"symbol": symbol}
    gene.update(GENE_DEFAULTS)
    return gene


def validate_gene(gene_dict: dict) -> list[str]:
    """Validate a gene dict against the schema.

    Returns list of validation errors (empty = valid).
    """
    errors = []

    # symbol must be a non-empty string
    symbol = gene_dict.get("symbol")
    if not isinstance(symbol, str) or not symbol:
        errors.append("symbol must be a non-empty string")

    # All _in_* flags must be bool
    for flag in SOURCE_FLAGS:
        if flag in gene_dict and not isinstance(gene_dict[flag], bool):
            errors.append(f"{flag} must be bool, got {type(gene_dict[flag]).__name__}")

    # All *_id fields must be str
    for field in GENE_DEFAULTS:
        if field.endswith("_id") and field in gene_dict:
            if not isinstance(gene_dict[field], str):
                errors.append(
                    f"{field} must be str, got {type(gene_dict[field]).__name__}"
                )

    # Optional fields, if present, must have correct types
    for field in OPTIONAL_FIELDS:
        if field in gene_dict:
            expected = OPTIONAL_FIELD_TYPES.get(field)
            if expected and not isinstance(gene_dict[field], expected):
                errors.append(
                    f"{field} must be {expected}, "
                    f"got {type(gene_dict[field]).__name__}"
                )

    return errors
