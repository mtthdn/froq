package example

// Source B: Disease phenotype database (2 of 3 genes — SOX9 is the gap)

genes: {
	"IRF6": {
		in_source_b: true
		source_b_id: "OMIM:607199"
		phenotypes: ["Cleft lip", "Cleft palate", "Lip pit"]
	}
	"PAX3": {
		in_source_b: true
		source_b_id: "OMIM:606597"
		phenotypes: ["Waardenburg syndrome", "White forelock", "Hearing loss"]
	}
	// SOX9 missing from source B — this is the gap
}
