
#!/usr/bin/env python3
import argparse, json, random
import pandas as pd
import numpy as np
from pathlib import Path
from utils import read_annotations, canon

def pairs_by_model_run(df: pd.DataFrame):
    # returns dict: (model, run) -> set of canonical pairs
    d = {}
    for (model, run), sub in df.groupby(['Model','Run']):
        s = set(sub['pair'])
        d[(str(model), int(run) if pd.notna(run) else -1)] = s
    return d

def full_catalog(df: pd.DataFrame, k: int):
    # distinct-model support across all 10 runs per model
    model_pair = df.groupby(['Model','pair']).size().reset_index(name='n')
    support = model_pair.groupby('pair')['Model'].nunique()
    return set(support[support >= k].index)

def sample_catalog(model_run_pairs: dict, k: int, per_model: int, rng: random.Random):
    # For each model, sample per_model runs without replacement; then compute distinct-model support
    # Build support dictionary: pair -> set(models)
    support = {}
    # Determine per-model runs available
    models = {}
    for (m,r), pairs in model_run_pairs.items():
        models.setdefault(m, []).append(((m,r), pairs))
    # Sample
    for m, items in models.items():
        if len(items) <= per_model:
            chosen = items
        else:
            chosen = rng.sample(items, per_model)
        # Gather pairs for this model
        union_pairs = set()
        for (_mr, prs) in chosen:
            union_pairs |= prs
        for p in union_pairs:
            support.setdefault(p, set()).add(m)
    # Threshold by number of distinct models
    return { p for p, ms in support.items() if len(ms) >= k }

def main():
    ap = argparse.ArgumentParser(description="Bootstrap Jaccard stability by sub-sampling runs per model.")
    ap.add_argument("--input", required=True, help="Annotations CSV")
    ap.add_argument("--k", type=int, default=5, help="Distinct-model threshold (default 5)")
    ap.add_argument("--draws", type=int, default=2000, help="Bootstrap draws (default 2000)")
    ap.add_argument("--per_model", type=int, default=5, help="Runs per model to sample (default 5 of 10)")
    ap.add_argument("--out", required=True, help="Output CSV with per-draw Jaccard overlaps")
    ap.add_argument("--summary", required=True, help="Output JSON summary (median, IQR)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    df = read_annotations(args.input)

    C_full = full_catalog(df, args.k)
    pr = pairs_by_model_run(df)

    rows = []
    for b in range(args.draws):
        C_b = sample_catalog(pr, args.k, args.per_model, rng)
        inter = len(C_b & C_full)
        union = len(C_b | C_full)
        j = (inter / union) if union else 1.0
        rows.append({"draw": b+1, "jaccard": j, "size_boot": len(C_b), "size_full": len(C_full)})
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)

    med = float(np.median(out['jaccard']))
    q1 = float(np.quantile(out['jaccard'], 0.25))
    q3 = float(np.quantile(out['jaccard'], 0.75))
    summary = {"k": args.k, "draws": args.draws, "per_model": args.per_model,
               "median_jaccard": med, "iqr": [q1, q3]}
    Path(args.summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
