
#!/usr/bin/env python3
import argparse, json
import pandas as pd
from pathlib import Path
from utils import read_annotations, distinct_model_support

def main():
    ap = argparse.ArgumentParser(description="Parse annotations and compute inter-model consensus shortlist.")
    ap.add_argument("--input", required=True, help="Path to Annotation_and_Mapping_Combined.csv")
    ap.add_argument("--k", type=int, default=5, help="Distinct-model support threshold (default: 5)")
    ap.add_argument("--outdir", required=True, help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = read_annotations(args.input)

    # Universe size
    universe = df['pair'].nunique()

    # Distinct-model support per pair
    support = distinct_model_support(df)
    support['class_canon'] = support['pair'].apply(lambda p: p[0])
    support['method_canon'] = support['pair'].apply(lambda p: p[1])

    # k-sweep coverage
    ks = list(range(1, 10))
    rows = []
    for k in ks:
        cnt = (support['support_models'] >= k).sum()
        rows.append({"k": k, "count": int(cnt)})
    sweep = pd.DataFrame(rows)
    sweep.to_csv(outdir / "k_sweep_coverage.csv", index=False)

    # shortlist at k
    shortlist = support[support['support_models'] >= args.k].copy()
    shortlist = shortlist.sort_values(['support_models','class_canon','method_canon'], ascending=[False, True, True])
    shortlist.to_csv(outdir / f"shortlist_k{args.k}.csv", index=False)

    # Save universe size
    with open(outdir / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"universe": int(universe), "k": args.k, "shortlist_size": int(len(shortlist))}, f, indent=2)

if __name__ == "__main__":
    main()
