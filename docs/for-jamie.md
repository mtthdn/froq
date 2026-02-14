# froq: What This Is and Where It Could Go

Jamie --

I assumed you'd want to see funding gaps first, so that's what I built. If I'm wrong about that, keep reading -- the underlying architecture does other things that might matter more to you.

## What You're Looking At

froq cross-references 95 neural crest genes across 12 public databases (Gene Ontology, OMIM, HPO, UniProt, FaceBase, ClinVar, PubMed, gnomAD, NIH Reporter, GTEx, ClinicalTrials.gov, STRING) and shows you the coverage in one place. The headline finding: 73 of those 95 genes have Mendelian disease associations in OMIM but zero experimental datasets in FaceBase. Whether that's interesting or obvious to you, I don't know -- but the data's there and it's verifiable. Click any gene and check.

## What It Does Now

- **Gap analysis** -- genes with disease relevance but no experimental coverage, ranked by weighted priority score (combines syndrome burden, phenotype count, constraint, publication scarcity)
- **Per-gene dossier** -- click any gene, see all 12 sources, publications with trend analysis, pathogenic variants, syndromes, tissue expression, active grants, genetic constraint, protein interactions
- **Understudied gene ranking** -- disease genes sorted by craniofacial publication count (ascending), with priority badges
- **Exportable briefing** -- generates a summary paragraph with top priority targets, copy to clipboard
- **CSV export templates** -- four presets: All Genes, Critical Gaps Only, Top Priority (score >= 15), Understudied (< 20 pubs). Full dataset, 19 columns, all 12 sources
- **Syndrome-centric view** -- flips the analysis from gene-level to disease-level. Instead of asking "which databases cover SOX10?", you ask "how well is Waardenburg syndrome covered?" Shows every multi-gene syndrome with FaceBase coverage, publication counts, and pathogenic variant totals. Click a syndrome to highlight all its genes in the graph.
- **Portfolio overlay** -- paste your funded gene targets and instantly see which critical gaps your portfolio covers vs. which remain unfunded. Separates covered gaps (green), unfunded gaps (red), and genes that are already well-covered. Useful for demonstrating portfolio impact or identifying complementary funding opportunities.
- **Cross-source filtering** -- interactive filter panel with tri-state toggle buttons for each database (any/required/excluded) plus numeric ranges for publication count and pathogenic variants. Ask questions like "every gene in OMIM but NOT in FaceBase with > 100 pathogenic variants" and get the filtered table instantly.
- **Gene table search** -- real-time search across gene symbols, syndromes, and protein names. Start typing and the table filters immediately.
- **Gene landscape graph** -- Cytoscape.js network visualization with 95 nodes and 2000+ edges across four relationship types: shared phenotypes, shared syndromes, shared GO biological processes, and STRING protein-protein interactions. Filter by edge type. Nodes colored by developmental role, sized by publication volume.
- **Tissue expression** -- GTEx expression data showing top tissues and craniofacial-specific TPM values in the gene detail panel
- **Active grants** -- NIH Reporter project details with PI names and direct links
- **Genetic constraint** -- gnomAD pLI and LOEUF scores with clinical interpretation (high/moderate/low intolerance to loss-of-function)
- **Clinical trials** -- active ClinicalTrials.gov studies per gene, surfacing which disease genes have active interventional research
- **Protein interactions** -- STRING database partners within the 95-gene network, clickable to navigate between connected genes
- **Publication trends** -- visual indicators (rising/stable/declining) based on recent-to-total publication ratio
- **Change history** -- the pipeline saves a snapshot of the gap state each time it runs. When multiple runs exist, you see which gaps opened or closed over time -- directly measuring the impact of NIDCR investments.

## What It Could Do That Your Tools Can't

These aren't built yet. I'm listing them so you can tell me which ones would actually be useful vs. which ones I'm imagining.

### 1. Temporal Impact Measurement

The change history is capturing snapshots. The next step is automated monthly runs and a richer trend view:

> "3 genes gained FaceBase data since last quarter. These 5 gap genes still have zero experimental coverage. Gap closure rate: 4% per quarter."

No existing tool tracks whether coverage gaps are closing over time. This directly measures the impact of NIDCR investments -- which is exactly what you'd need to justify portfolio decisions to leadership.

### 2. Pathway Enrichment Analysis

The graph shows which genes share biological processes, but doesn't yet compute statistical enrichment. A Fisher's exact test against GO biological processes would answer: "Which pathways are over-represented among the gap genes?" -- shifting the conversation from individual genes to biological themes.

### 3. PDF Dossiers

The CSV export covers raw data. A formatted PDF dossier for a specific gene or set of genes -- with the gap analysis, publication timeline, syndrome associations, and tissue expression in a printable layout -- would be directly usable in grant applications.

## How It Works (30-Second Version)

Each database is queried by a Python script that caches the raw data and writes it into a typed data file. [CUE](https://cuelang.org/) (a data language) merges all 12 sources per gene using lattice unification -- each source owns its own fields, the merge is structural and type-safe. A generator reads the unified model and produces the site.

The whole pipeline is reproducible from cached data. No manual curation, no spreadsheet joins.

## What I Need From You

Honestly? Just tell me if any of this is useful or if I'm solving a problem you don't have. The temporal impact measurement and pathway enrichment are the two I think would matter most, but I've been wrong before.

-- Matt

---

*The methodology and all database references are on the About page.*
