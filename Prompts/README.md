# Prompts & originating inputs

This folder contains the *originating artifacts* used to obtain the raw LLM generations:

- `Prompt.txt` — exact prompt used for all models/runs
- `Methodless.txt` — PlantUML for the method-free UML scaffold
- `UC.txt` — the 21 structured use cases (concatenated)

These files are included for **provenance and auditability**. The deterministic pipeline in `src/`
starts from `data/Annotation_and_Mapping_Combined.csv` and reproduces the consensus results without
calling external models.
