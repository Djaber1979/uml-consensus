
#!/usr/bin/env python3
import argparse, json
import pandas as pd
from pathlib import Path
from utils import read_annotations, uc_select_for_pair, representative_raw_method, representative_raw_class

def main():
    ap = argparse.ArgumentParser(description="Select UC tag deterministically for catalog pairs.")
    ap.add_argument("--input", required=True, help="Original annotations CSV (for tag votes)")
    ap.add_argument("--catalog", required=True, help="Catalog CSV after merges (from apply_expert_merges.py)")
    ap.add_argument("--k", type=int, default=5, help="Distinct-model threshold for UC consensus (default 5)")
    ap.add_argument("--out", required=True, help="Output CSV with UC selection")
    args = ap.parse_args()

    df = read_annotations(args.input)
    cat = pd.read_csv(args.catalog)
    cat['pair'] = list(zip(cat['class_canon'], cat['method_canon']))

    selected_uc = []
    rep_method = []
    rep_class = []
    selection_mode = []

    for _, row in cat.iterrows():
        pair = (row['class_canon'], row['method_canon'])
        uc, mode = uc_select_for_pair(df, pair, k_models=args.k)
        selected_uc.append(uc)
        selection_mode.append(mode)
        rep_method.append(representative_raw_method(df, pair))
        rep_class.append(representative_raw_class(df, pair))

    out = cat.copy()
    out['RepresentativeClassRaw']  = rep_class
    out['RepresentativeMethodRaw'] = rep_method
    out['SelectedUC'] = selected_uc
    out['UCSelectionMode'] = selection_mode

    out.to_csv(args.out, index=False)

if __name__ == "__main__":
    main()
