
#!/usr/bin/env python3
import argparse, json
import pandas as pd
from pathlib import Path
from utils import canon

def main():
    ap = argparse.ArgumentParser(description="Apply expert merges/duplicate removals to shortlist.")
    ap.add_argument("--shortlist", required=True, help="shortlist_kX.csv from parse_and_consensus")
    ap.add_argument("--merges", required=True, help="expert_merges.csv")
    ap.add_argument("--out", required=True, help="Output CSV (catalog after merges)")
    args = ap.parse_args()

    sl = pd.read_csv(args.shortlist)
    merges = pd.read_csv(args.merges)

    # Build removal set from merges table
    to_remove = set()
    for _, row in merges.iterrows():
        c = canon(str(row['class']))
        rem = canon(str(row['remove']))
        t = str(row['type']).strip().lower()
        if t == "within-class":
            to_remove.add( (c, rem) )
        elif t == "cross-class-duplicate":
            # remove specific (class, method) pair
            to_remove.add( (c, rem) )
        else:
            to_remove.add( (c, rem) )

    before = len(sl)
    sl['pair'] = list(zip(sl['class_canon'], sl['method_canon']))
    sl = sl[~sl['pair'].isin(to_remove)].copy()
    sl.drop(columns=['pair'], inplace=True, errors='ignore')
    after = len(sl)

    sl.to_csv(args.out, index=False)

    meta = {"before": int(before), "after": int(after), "removed": int(before - after)}
    with open(Path(args.out).with_suffix(".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    main()
