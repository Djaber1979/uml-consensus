
PY=python3

DATA=data/Annotation_and_Mapping_Combined.csv
MERGES=data/expert_merges.csv
OUT=outputs

K?=5
DRAWS?=2000
PER_MODEL?=5

all: consensus merges uc enriched puml bootstrap

consensus:
	$(PY) src/parse_and_consensus.py --input $(DATA) --k $(K) --outdir $(OUT)

merges: consensus
	$(PY) src/apply_expert_merges.py --shortlist $(OUT)/shortlist_k$(K).csv --merges $(MERGES) --out $(OUT)/catalog_after_merges.csv

uc: merges
	$(PY) src/uc_selection.py --input $(DATA) --catalog $(OUT)/catalog_after_merges.csv --k $(K) --out $(OUT)/catalog_with_uc.csv

enriched: uc
	$(PY) src/export_enriched_detailed.py --input $(DATA) --catalog_uc $(OUT)/catalog_with_uc.csv --out $(OUT)/consensus_enriched_detailed.csv

puml: uc
	$(PY) src/plantuml_from_catalog.py --input $(OUT)/catalog_with_uc.csv --output $(OUT)/consensus_catalog.puml

bootstrap: consensus
	$(PY) src/bootstrap_jaccard.py --input $(DATA) --k $(K) --draws $(DRAWS) --per_model $(PER_MODEL) --out $(OUT)/bootstrap_jaccard.csv --summary $(OUT)/bootstrap_jaccard_summary.json

clean:
	rm -f $(OUT)/*.csv $(OUT)/*.json $(OUT)/*.puml
