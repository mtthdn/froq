# froq: What This Is and Where It Could Go

Jamie --

I assumed you'd want to see funding gaps first, so that's what I built. If I'm wrong about that, keep reading -- the underlying architecture does other things that might matter more to you.

## What You're Looking At

froq cross-references 95 neural crest genes across 7 public databases (Gene Ontology, OMIM, HPO, UniProt, FaceBase, ClinVar, PubMed) and shows you the coverage in one place. The headline finding: 73 of those 95 genes have Mendelian disease associations in OMIM but zero experimental datasets in FaceBase. Whether that's interesting or obvious to you, I don't know -- but the data's there and it's verifiable. Click any gene and check.

## What It Does Now

- **Gap analysis** -- genes with disease relevance but no experimental coverage
- **Per-gene dossier** -- click any gene, see all 7 sources, publications, pathogenic variants, syndromes, connected genes
- **Understudied gene ranking** -- disease genes sorted by craniofacial publication count (ascending)
- **Exportable briefing** -- generates a summary paragraph with top priority targets, copy to clipboard
- **CSV export** -- full dataset, 14 columns, all 7 sources
- **Syndrome-centric view** -- flips the analysis from gene-level to disease-level. Instead of asking "which databases cover SOX10?", you ask "how well is Waardenburg syndrome covered?" Shows every multi-gene syndrome with FaceBase coverage, publication counts, and pathogenic variant totals. Click a syndrome to highlight all its genes in the graph.
- **Portfolio overlay** -- paste your funded gene targets and instantly see which critical gaps your portfolio covers vs. which remain unfunded. Separates covered gaps (green), unfunded gaps (red), and genes that are already well-covered. Useful for demonstrating portfolio impact or identifying complementary funding opportunities.
- **Cross-source filtering** -- interactive filter panel with tri-state toggle buttons for each database (any/required/excluded) plus numeric ranges for publication count and pathogenic variants. Ask questions like "every gene in OMIM but NOT in FaceBase with > 100 pathogenic variants" and get the filtered table instantly.
- **Gene table search** -- real-time search across gene symbols, syndromes, and protein names. Start typing and the table filters immediately.
- **Graph edge tooltips** -- hover over any edge in the gene landscape graph to see the syndrome or phenotype that connects two genes.
- **Change history (scaffolded)** -- the pipeline saves a snapshot of the gap state each time it runs. Once we have a few runs, you'll see which gaps opened or closed over time -- directly measuring the impact of NIDCR investments. Right now it shows a baseline capture.

## What It Could Do That Your Tools Can't

These aren't built yet. I'm listing them so you can tell me which ones would actually be useful vs. which ones I'm imagining.

### 1. Temporal Diffing (full)

The scaffold is in place -- the pipeline already saves snapshots. The next step is automated monthly runs and a richer diff UI:

> "3 genes gained FaceBase data since last quarter. These 5 gap genes still have zero experimental coverage. Gap closure rate: 4% per quarter."

No existing tool tracks whether coverage gaps are closing over time. This directly measures the impact of NIDCR investments -- which is exactly what you'd need to justify portfolio decisions to leadership.

### 2. New Databases

Adding a source is one Python script + a few lines of schema. Possible additions:

- **ClinicalTrials.gov** -- are there active trials for these genes? Disease association + pathogenic variants + no active trials = another type of gap
- **gnomAD** -- population allele frequencies for pathogenic variants. High frequency + pathogenic = higher population impact
- **NIH Reporter** -- map active NIH grants to gene targets. See which gaps have funded projects vs. which are truly orphaned
- **GTEx** -- tissue expression data. Which gap genes are actually expressed in craniofacial tissues?

Each new source makes every existing query richer because the data unifies automatically.

## How It Works (30-Second Version)

Each database is queried by a Python script that caches the raw data and writes it into a typed data file. [CUE](https://cuelang.org/) (a data language) merges all 7 sources per gene using lattice unification -- each source owns its own fields, the merge is structural and type-safe. A generator reads the unified model and produces the site.

The whole pipeline is reproducible from cached data. No manual curation, no spreadsheet joins.

## What I Need From You

Honestly? Just tell me if any of this is useful or if I'm solving a problem you don't have. The temporal diffing and new databases are the two I think would matter most, but I've been wrong before.

-- Matt

---

*The methodology and all database references are on the About page.*
