package froq

// Weighted gap priority scoring for NIDCR funding decisions.
// Higher score = stronger case for new funding.
//
// Components:
//   +5 per OMIM syndrome
//   +3 if >10 HPO phenotypes
//   +10 if NO FaceBase data (the key gap)
//   +3 if high constraint (pLI > 0.9)
//   +1 if understudied (<10 publications)

weighted_gaps: {for k, v in genes {
	(k): {
		symbol: k

		// Syndrome burden — safe: len() is in body, not guard
		_syn_count: *0 | int
		if v.omim_syndromes != _|_ {_syn_count: len(v.omim_syndromes)}
		_syndrome_score: _syn_count * 5

		// Rich phenotype data — intermediate avoids optional ref in guard
		_pheno_count: *0 | int
		if v.phenotypes != _|_ {_pheno_count: len(v.phenotypes)}
		_pheno_score: *0 | int
		if v._in_hpo && _pheno_count > 10 {_pheno_score: 3}

		// THE key gap: no FaceBase experimental data
		_facebase_gap: *0 | int
		if !v._in_facebase {_facebase_gap: 10}

		// High constraint — intermediate avoids optional ref in guard
		_pli: *0.0 | number
		if v.pli_score != _|_ {_pli: v.pli_score}
		_constraint_score: *0 | int
		if _pli > 0.9 {_constraint_score: 3}

		// Understudied in literature — intermediate avoids optional ref in guard
		_pub_total: *-1 | int
		if v.pubmed_total != _|_ {_pub_total: v.pubmed_total}
		_pub_score: *0 | int
		if _pub_total >= 0 && _pub_total < 10 {_pub_score: 1}
		if _pub_total < 0 {_pub_score: 1}

		// Composite priority
		priority_score: _syndrome_score + _pheno_score + _facebase_gap + _constraint_score + _pub_score

		// Metadata for display
		has_disease:    v._in_omim
		has_experiment: v._in_facebase
		if v.omim_syndromes != _|_ {syndrome_count: len(v.omim_syndromes)}
		if v.pubmed_total != _|_ {pub_count: v.pubmed_total}
		if v.pathogenic_count != _|_ {variant_count: v.pathogenic_count}
		if v.pli_score != _|_ {pli_score: v.pli_score}
		if v.active_grant_count != _|_ {grant_count: v.active_grant_count}
	}
}}
