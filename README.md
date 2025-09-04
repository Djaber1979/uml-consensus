# UML Behavior Consensus (Reproducible Repo)

This repository reconstructs the **inter-model consensus** pipeline over the uploaded annotation file and applies the **expert merges** to produce a final catalog with **deterministic UC selection** and a PlantUML export.

- Input: `data/Annotation_and_Mapping_Combined.csv` (uploaded; semicolon-separated).
- Expert merges: `data/expert_merges.csv` (from the paper's adjudication table; includes 6 within-class synonyms and 1 cross-class duplicate removal).  
- Output artifacts are written into `outputs/`.

## Originating artifacts (prompts & inputs)

The upstream inputs used during the original LLM runs are included under `prompts/`:

- `prompts/Prompt.txt` — the exact prompt text
- `prompts/Methodless.txt` — method-free UML scaffold (PlantUML)
- `prompts/UC.txt` — the 21 structured use cases

These are provided for **provenance**. The deterministic pipeline in `src/` does **not** consume these files; it starts from
`data/Annotation_and_Mapping_Combined.csv` and reproduces all tables and figures deterministically.

## Quick start

```bash
# (optional) create and activate a virtualenv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline at the default threshold k=5
make all

# Individual steps
make consensus   # k-sweep + shortlist
make merges      # apply merges -> catalog_after_merges.csv
make uc          # deterministic UC selection
make enriched    # detailed CSV with raw inventories
make puml        # PlantUML source with bold red UC notes per method
make bootstrap  # bootstrap Jaccard stability (2000 draws; 5 runs/model by default)

```

## Outputs

- `outputs/k_sweep_coverage.csv` — coverage of C_>=k across k=1..9  
- `outputs/shortlist_k5.csv` — shortlist at k=5 (distinct-model support)  
- `outputs/catalog_after_merges.csv` — after applying expert merges  
- `outputs/catalog_with_uc.csv` — catalog + deterministic UC selection  
- `outputs/consensus_enriched_detailed.csv` — enriched detailed table with raw name inventories, action inventories, and UC vote distributions  
- `outputs/consensus_catalog.puml` — PlantUML class diagram source; UC tags are rendered inline, immediately after each method name:
  `+ methodName() {<b><color:red>UCxx</color></b>}` (no `UC=` prefix).
- `outputs/bootstrap_jaccard.csv` — per-draw Jaccard overlaps for the k=5 catalog (default: 2000 draws; 5 runs/model).
- `outputs/bootstrap_jaccard_summary.json` — summary statistics (k, draws, per_model, median_jaccard, IQR).
- `outputs/meta.json` — run metadata (e.g., shortlist_size and k).


> Note: The adjudication table here exactly encodes the expert decisions in the manuscript. Depending on exact naming variants in the annotation file (e.g., `cancelRequest` vs `cancelServiceRequest`), only a subset of merges may apply; the pipeline stays deterministic.

## Determinism and rules

- **Canonicalization**: lower-case + removal of non-alphanumerics for class and method identifiers (used only for aggregation).  
- **Support counting**: number of **distinct models** that emitted a pair in any run.  
- **UC selection (per pair)**:
  1. If any UC attains ≥k distinct-model support, choose among those by **higher model support**, then **higher instance count**, then **smaller UC number**.
  2. Otherwise, choose by **highest instance count**; tie by **higher model support**, then **smaller UC number**.
 - **Actions are not used in any calculation.** Action phrases are **never** used for consensus or UC selection; they are listed only in the enriched CSV for reference.
 

- **PlantUML export**: for each method we append `{<b><color:red>UCxx</color></b>}` **inline immediately after the method name**. Tags are bold/red, and no `UC=` prefix is used.

## Data & Code Licenses

- Code: MIT License (see `LICENSE`).  
- Data (derived from your upload): CC-BY-4.0 (see `DATA_LICENSE`).

## Reproducing the paper numbers

The `Makefile` re-computes coverage and the shortlist directly from `data/Annotation_and_Mapping_Combined.csv`. The provided `data/expert_merges.csv` encodes the expert decisions from the paper. If you wish to experiment with alternative merges or thresholds, edit `data/expert_merges.csv` or run `make K=6 all` for a different support tier.
