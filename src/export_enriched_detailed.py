
#!/usr/bin/env python3
import argparse, json
import pandas as pd
from pathlib import Path
from collections import defaultdict
from utils import read_annotations

def main():
    ap = argparse.ArgumentParser(description="Create enriched detailed CSV with raw names, actions, and per-UC tallies.")
    ap.add_argument("--input", required=True, help="Original annotations CSV")
    ap.add_argument("--catalog_uc", required=True, help="Catalog with SelectedUC (from uc_selection.py)")
    ap.add_argument("--out", required=True, help="Output CSV (enriched detailed)")
    args = ap.parse_args()

    df = read_annotations(args.input)
    cat = pd.read_csv(args.catalog_uc)
    cat['pair'] = list(zip(cat['class_canon'], cat['method_canon']))

    # Build aggregates for raw names and actions
    records = []
    for _, row in cat.iterrows():
        pair = (row['class_canon'], row['method_canon'])
        sub = df[df['pair']==pair].copy()
        # Raw name inventories
        raw_classes = sub['Class'].dropna().value_counts().to_dict()
        raw_methods = sub['MethodName'].dropna().value_counts().to_dict()
        actions = sub['UC_Action'].dropna().value_counts().to_dict()
        # UC distributions
        uc_inst = sub['UC_tag'].dropna().value_counts().to_dict()
        mp = sub.dropna(subset=['UC_tag']).groupby(['UC_tag','Model']).size().reset_index(name='n')
        uc_models = mp.groupby('UC_tag')['Model'].nunique().to_dict()

        rec = dict(row)
        rec['RawClassInventory'] = "; ".join([f"{k} (n={v})" for k,v in raw_classes.items()])
        rec['RawMethodInventory'] = "; ".join([f"{k} (n={v})" for k,v in raw_methods.items()])
        rec['ActionInventory'] = "; ".join([f"{k} (n={v})" for k,v in actions.items()])
        rec['UCInstanceCounts'] = "; ".join([f"{k}:{v}" for k,v in uc_inst.items()])
        rec['UCModelCounts'] = "; ".join([f"{k}:{v}" for k,v in uc_models.items()])
        records.append(rec)

    out = pd.DataFrame.from_records(records)
    out.to_csv(args.out, index=False)

if __name__ == "__main__":
    main()
