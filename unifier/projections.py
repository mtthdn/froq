"""Python reimplementations of CUE projection files.

Each function takes the unified gene dict (with _in_* source flags merged in)
and produces output identical to the corresponding CUE projection expression.

All 6 projections have been verified byte-for-byte identical to CUE output.
"""


def project_gene_sources(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e gene_sources

    Exports the _in_* hidden flags as visible fields.
    """
    result = {}
    for symbol, gene in sorted(unified.items()):
        result[symbol] = {
            "in_go": gene.get("_in_go", False),
            "in_omim": gene.get("_in_omim", False),
            "in_hpo": gene.get("_in_hpo", False),
            "in_uniprot": gene.get("_in_uniprot", False),
            "in_facebase": gene.get("_in_facebase", False),
            "in_clinvar": gene.get("_in_clinvar", False),
            "in_pubmed": gene.get("_in_pubmed", False),
            "in_gnomad": gene.get("_in_gnomad", False),
            "in_nih_reporter": gene.get("_in_nih_reporter", False),
            "in_gtex": gene.get("_in_gtex", False),
            "in_clinicaltrials": gene.get("_in_clinicaltrials", False),
            "in_string": gene.get("_in_string", False),
        }
    return result


def project_enrichment(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e enrichment"""
    tiers = {}
    for symbol, gene in sorted(unified.items()):
        tiers[symbol] = {
            "has_function": gene.get("_in_go", False),
            "has_disease": gene.get("_in_omim", False),
            "has_phenotype": gene.get("_in_hpo", False),
            "has_protein": gene.get("_in_uniprot", False),
            "has_experiment": gene.get("_in_facebase", False),
            "has_variants": gene.get("_in_clinvar", False),
            "has_literature": gene.get("_in_pubmed", False),
            "has_constraint": gene.get("_in_gnomad", False),
            "has_funding": gene.get("_in_nih_reporter", False),
            "has_expression": gene.get("_in_gtex", False),
            "has_trials": gene.get("_in_clinicaltrials", False),
            "has_interactions": gene.get("_in_string", False),
        }
    return {"tiers": tiers}


def project_gap_report(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e gap_report"""
    genes = unified

    # Per-source missing lists
    missing_go = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_go", False)]
    missing_omim = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_omim", False)]
    missing_hpo = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_hpo", False)]
    missing_uniprot = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_uniprot", False)]
    missing_facebase = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_facebase", False)]
    missing_clinvar = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_clinvar", False)]
    missing_pubmed = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_pubmed", False)]
    missing_gnomad = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_gnomad", False)]
    missing_nih_reporter = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_nih_reporter", False)]
    missing_gtex = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_gtex", False)]
    missing_clinicaltrials = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_clinicaltrials", False)]
    missing_string = [{"symbol": k} for k in sorted(genes) if not genes[k].get("_in_string", False)]

    # All-N lists
    all_five = sorted([
        k for k, v in genes.items()
        if v.get("_in_go") and v.get("_in_omim") and v.get("_in_hpo")
        and v.get("_in_uniprot") and v.get("_in_facebase")
    ])
    all_seven = sorted([
        k for k, v in genes.items()
        if v.get("_in_go") and v.get("_in_omim") and v.get("_in_hpo")
        and v.get("_in_uniprot") and v.get("_in_facebase")
        and v.get("_in_clinvar") and v.get("_in_pubmed")
    ])
    all_ten = sorted([
        k for k, v in genes.items()
        if v.get("_in_go") and v.get("_in_omim") and v.get("_in_hpo")
        and v.get("_in_uniprot") and v.get("_in_facebase")
        and v.get("_in_clinvar") and v.get("_in_pubmed")
        and v.get("_in_gnomad") and v.get("_in_nih_reporter")
        and v.get("_in_gtex")
    ])

    # Research gaps
    research_gaps = []
    for k in sorted(genes):
        v = genes[k]
        if v.get("_in_omim") and not v.get("_in_facebase"):
            entry = {"symbol": k}
            if "omim_syndromes" in v:
                entry["syndromes"] = v["omim_syndromes"]
            research_gaps.append(entry)

    return {
        "summary": {
            "total": len(genes),
            "in_all_five": len(all_five),
            "in_all_seven": len(all_seven),
            "in_all_ten": len(all_ten),
            "missing_go_count": len(missing_go),
            "missing_omim_count": len(missing_omim),
            "missing_hpo_count": len(missing_hpo),
            "missing_uniprot_count": len(missing_uniprot),
            "missing_facebase_count": len(missing_facebase),
            "missing_clinvar_count": len(missing_clinvar),
            "missing_pubmed_count": len(missing_pubmed),
            "missing_gnomad_count": len(missing_gnomad),
            "missing_nih_reporter_count": len(missing_nih_reporter),
            "missing_gtex_count": len(missing_gtex),
            "missing_clinicaltrials_count": len(missing_clinicaltrials),
            "missing_string_count": len(missing_string),
        },
        "research_gaps": research_gaps,
        "missing_go": missing_go,
        "missing_omim": missing_omim,
        "missing_hpo": missing_hpo,
        "missing_uniprot": missing_uniprot,
        "missing_facebase": missing_facebase,
        "missing_clinvar": missing_clinvar,
        "missing_pubmed": missing_pubmed,
        "missing_gnomad": missing_gnomad,
        "missing_nih_reporter": missing_nih_reporter,
        "missing_gtex": missing_gtex,
        "missing_clinicaltrials": missing_clinicaltrials,
        "missing_string": missing_string,
    }


def project_funding_gaps(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e funding_gaps"""
    genes = unified

    genes_assessed = {}
    for k in sorted(genes):
        v = genes[k]
        entry = {
            "symbol": k,
            "has_disease": v.get("_in_omim", False),
            "has_phenotype": v.get("_in_hpo", False),
            "has_experiment": v.get("_in_facebase", False),
            "has_variants": v.get("_in_clinvar", False),
            "has_literature": v.get("_in_pubmed", False),
            "has_constraint": v.get("_in_gnomad", False),
            "has_funding": v.get("_in_nih_reporter", False),
            "has_expression": v.get("_in_gtex", False),
            "has_trials": v.get("_in_clinicaltrials", False),
            "has_interactions": v.get("_in_string", False),
            "pub_count": v.get("pubmed_total", 0),
        }
        if "omim_syndromes" in v:
            entry["syndromes"] = v["omim_syndromes"]
        if "pathogenic_count" in v:
            entry["variant_count"] = v["pathogenic_count"]
        if "pli_score" in v:
            entry["pli_score"] = v["pli_score"]
        if "active_grant_count" in v:
            entry["grant_count"] = v["active_grant_count"]
        genes_assessed[k] = entry

    critical = []
    for k in sorted(genes):
        v = genes[k]
        if v.get("_in_omim") and not v.get("_in_facebase"):
            entry = {"symbol": k}
            if "omim_syndromes" in v:
                entry["syndromes"] = v["omim_syndromes"]
            entry["pub_count"] = v.get("pubmed_total", 0)
            if "phenotypes" in v:
                entry["phenotype_count"] = len(v["phenotypes"])
            if "pathogenic_count" in v:
                entry["variant_count"] = v["pathogenic_count"]
            if "pli_score" in v:
                entry["pli_score"] = v["pli_score"]
            if "active_grant_count" in v:
                entry["grant_count"] = v["active_grant_count"]
            critical.append(entry)

    return {
        "genes_assessed": genes_assessed,
        "critical": critical,
        "summary": {
            "total_genes": len(genes),
            "critical_count": len(critical),
        },
    }


def project_weighted_gaps(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e weighted_gaps"""
    result = {}
    for k in sorted(unified):
        v = unified[k]

        # Syndrome burden
        syn_count = len(v["omim_syndromes"]) if "omim_syndromes" in v else 0
        syndrome_score = syn_count * 5

        # Phenotype richness
        pheno_count = len(v["phenotypes"]) if "phenotypes" in v else 0
        pheno_score = 3 if (v.get("_in_hpo") and pheno_count > 10) else 0

        # FaceBase gap
        facebase_gap = 0 if v.get("_in_facebase") else 10

        # Constraint
        pli = v.get("pli_score", 0.0) if "pli_score" in v else 0.0
        constraint_score = 3 if pli > 0.9 else 0

        # Understudied
        pub_total = v.get("pubmed_total", -1) if "pubmed_total" in v else -1
        if pub_total >= 0 and pub_total < 10:
            pub_score = 1
        elif pub_total < 0:
            pub_score = 1
        else:
            pub_score = 0

        priority_score = syndrome_score + pheno_score + facebase_gap + constraint_score + pub_score

        entry = {
            "symbol": k,
            "priority_score": priority_score,
            "has_disease": v.get("_in_omim", False),
            "has_experiment": v.get("_in_facebase", False),
        }
        if "omim_syndromes" in v:
            entry["syndrome_count"] = len(v["omim_syndromes"])
        if "pubmed_total" in v:
            entry["pub_count"] = v["pubmed_total"]
        if "pathogenic_count" in v:
            entry["variant_count"] = v["pathogenic_count"]
        if "pli_score" in v:
            entry["pli_score"] = v["pli_score"]
        if "active_grant_count" in v:
            entry["grant_count"] = v["active_grant_count"]

        result[k] = entry

    return result


def project_anomalies(unified: dict) -> dict:
    """Equivalent to: cue export ./model/ -e anomalies"""
    genes = unified

    # Build anomaly input intermediates (mirrors _anomaly_input in CUE)
    omim_no_clinvar = []
    high_pli_no_trials = []
    high_pubs_no_facebase = []
    clinvar_no_hpo = []

    for k in sorted(genes):
        v = genes[k]

        has_omim = v.get("_in_omim", False)
        has_facebase = v.get("_in_facebase", False)
        has_hpo = v.get("_in_hpo", False)

        syn_count = len(v["omim_syndromes"]) if "omim_syndromes" in v else 0
        pathogenic = v.get("pathogenic_count", 0) if "pathogenic_count" in v else 0
        pli = v.get("pli_score", 0.0) if "pli_score" in v else 0.0
        trial_count = v.get("active_trial_count", 0) if "active_trial_count" in v else 0
        pub_total = v.get("pubmed_total", 0) if "pubmed_total" in v else 0
        pheno_count = len(v["phenotypes"]) if "phenotypes" in v else 0
        has_pli = "pli_score" in v

        # Rule 1: OMIM disease but 0 ClinVar pathogenic variants
        if has_omim and syn_count > 0 and pathogenic == 0:
            entry = {
                "symbol": k,
                "anomaly_type": "omim_no_clinvar",
                "description": "Has OMIM disease association but 0 ClinVar pathogenic variants",
                "severity": "warning",
            }
            if "omim_syndromes" in v:
                entry["syndromes"] = v["omim_syndromes"]
            omim_no_clinvar.append(entry)

        # Rule 2: High pLI but no clinical trials
        if has_pli and pli > 0.9 and trial_count == 0:
            entry = {
                "symbol": k,
                "anomaly_type": "high_pli_no_trials",
                "description": "Highly constrained (pLI > 0.9) but no active clinical trials",
                "severity": "info",
            }
            if "pli_score" in v:
                entry["pli_score"] = v["pli_score"]
            high_pli_no_trials.append(entry)

        # Rule 3: High publication count but no FaceBase
        if pub_total > 500 and not has_facebase:
            entry = {
                "symbol": k,
                "anomaly_type": "high_pubs_no_facebase",
                "description": "Over 500 publications but no FaceBase experimental data",
                "severity": "warning",
            }
            if "pubmed_total" in v:
                entry["pub_count"] = v["pubmed_total"]
            high_pubs_no_facebase.append(entry)

        # Rule 4: ClinVar pathogenic variants but no HPO phenotypes
        if pathogenic > 10 and pheno_count == 0:
            entry = {
                "symbol": k,
                "anomaly_type": "clinvar_no_hpo",
                "description": "Over 10 pathogenic variants but no HPO phenotypes listed",
                "severity": "error",
            }
            if "pathogenic_count" in v:
                entry["pathogenic_count"] = v["pathogenic_count"]
            clinvar_no_hpo.append(entry)

    all_anomalies = omim_no_clinvar + high_pli_no_trials + high_pubs_no_facebase + clinvar_no_hpo

    return {
        "genes_with_anomalies": all_anomalies,
        "summary": {
            "total_anomalies": len(all_anomalies),
            "omim_no_clinvar_count": len(omim_no_clinvar),
            "high_pli_no_trials_count": len(high_pli_no_trials),
            "high_pubs_no_facebase_count": len(high_pubs_no_facebase),
            "clinvar_no_hpo_count": len(clinvar_no_hpo),
        },
    }


# ---------------------------------------------------------------------------
# Projection registry
# ---------------------------------------------------------------------------

ALL_PROJECTIONS = {
    "gene_sources": project_gene_sources,
    "enrichment": project_enrichment,
    "gap_report": project_gap_report,
    "funding_gaps": project_funding_gaps,
    "weighted_gaps": project_weighted_gaps,
    "anomalies": project_anomalies,
}


def compute_all(unified: dict) -> dict:
    """Run every projection and return {name: result}."""
    return {name: fn(unified) for name, fn in ALL_PROJECTIONS.items()}
