package froq

import "list"

// Cross-source anomaly detection: flags inconsistencies between
// biomedical databases that may indicate data gaps, annotation
// problems, or therapeutic opportunities.
//
// Uses intermediate defaulted fields to avoid referencing optional
// fields in comprehension guards (CUE constraint).

// Pre-compute safe intermediates for each gene.
_anomaly_input: {for k, v in genes {
	(k): {
		symbol: k

		// Source presence (non-optional booleans)
		_has_omim:     v._in_omim
		_has_facebase: v._in_facebase
		_has_hpo:      v._in_hpo

		// Safe intermediates for optional fields
		_syn_count: *0 | int
		if v.omim_syndromes != _|_ {_syn_count: len(v.omim_syndromes)}

		_pathogenic: *0 | int
		if v.pathogenic_count != _|_ {_pathogenic: v.pathogenic_count}

		_pli: *0.0 | number
		if v.pli_score != _|_ {_pli: v.pli_score}

		_trial_count: *0 | int
		if v.active_trial_count != _|_ {_trial_count: v.active_trial_count}

		_pub_total: *0 | int
		if v.pubmed_total != _|_ {_pub_total: v.pubmed_total}

		_pheno_count: *0 | int
		if v.phenotypes != _|_ {_pheno_count: len(v.phenotypes)}

		_has_pli: *false | bool
		if v.pli_score != _|_ {_has_pli: true}

		// Carry through display metadata
		if v.omim_syndromes != _|_ {syndromes: v.omim_syndromes}
		if v.pli_score != _|_ {pli_score: v.pli_score}
		if v.pubmed_total != _|_ {pub_count: v.pubmed_total}
		if v.pathogenic_count != _|_ {pathogenic_count: v.pathogenic_count}
	}
}}

anomalies: {
	// Rule 1: OMIM disease but 0 ClinVar pathogenic variants
	// Gene has omim_syndromes but pathogenic_count == 0 (possible data gap)
	_omim_no_clinvar: [for k, v in _anomaly_input
		if v._has_omim && v._syn_count > 0 && v._pathogenic == 0 {
		symbol:       k
		anomaly_type: "omim_no_clinvar"
		description:  "Has OMIM disease association but 0 ClinVar pathogenic variants"
		severity:     "warning"
		if v.syndromes != _|_ {syndromes: v.syndromes}
	}]

	// Rule 2: High pLI but no clinical trials
	// pli_score > 0.9 (highly constrained) but active_trial_count == 0
	_high_pli_no_trials: [for k, v in _anomaly_input
		if v._has_pli && v._pli > 0.9 && v._trial_count == 0 {
		symbol:       k
		anomaly_type: "high_pli_no_trials"
		description:  "Highly constrained (pLI > 0.9) but no active clinical trials"
		severity:     "info"
		if v.pli_score != _|_ {pli_score: v.pli_score}
	}]

	// Rule 3: High publication count but no FaceBase coverage
	// pubmed_total > 500 but _in_facebase == false
	_high_pubs_no_facebase: [for k, v in _anomaly_input
		if v._pub_total > 500 && !v._has_facebase {
		symbol:       k
		anomaly_type: "high_pubs_no_facebase"
		description:  "Over 500 publications but no FaceBase experimental data"
		severity:     "warning"
		if v.pub_count != _|_ {pub_count: v.pub_count}
	}]

	// Rule 4: ClinVar pathogenic variants but no HPO phenotypes
	// pathogenic_count > 10 but no phenotypes listed
	_clinvar_no_hpo: [for k, v in _anomaly_input
		if v._pathogenic > 10 && v._pheno_count == 0 {
		symbol:       k
		anomaly_type: "clinvar_no_hpo"
		description:  "Over 10 pathogenic variants but no HPO phenotypes listed"
		severity:     "error"
		if v.pathogenic_count != _|_ {pathogenic_count: v.pathogenic_count}
	}]

	// Combined list of all anomalies
	genes_with_anomalies: list.Concat([_omim_no_clinvar, _high_pli_no_trials, _high_pubs_no_facebase, _clinvar_no_hpo])

	// Summary counts per anomaly type
	summary: {
		total_anomalies:             len(genes_with_anomalies)
		omim_no_clinvar_count:       len(_omim_no_clinvar)
		high_pli_no_trials_count:    len(_high_pli_no_trials)
		high_pubs_no_facebase_count: len(_high_pubs_no_facebase)
		clinvar_no_hpo_count:        len(_clinvar_no_hpo)
	}
}
