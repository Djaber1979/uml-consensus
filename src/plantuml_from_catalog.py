
#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path
from collections import defaultdict
import re

def sanitize_id(s: str) -> str:
    # PlantUML identifier: allow letters, digits, underscore; replace others with _
    if s is None:
        return ""
    s2 = re.sub(r'[^A-Za-z0-9_]', '_', str(s))
    if not s2:
        s2 = "X"
    return s2

def ensure_parens(m: str) -> str:
    m = m.strip()
    if not m.endswith(")"):
        if "(" not in m:
            m = m + "()"
    return m

def main():
    ap = argparse.ArgumentParser(description="Generate PlantUML with inline bold/red UC tags after methods.")
    ap.add_argument("--input", required=True, help="CSV from uc_selection.py (RepresentativeClassRaw, RepresentativeMethodRaw, SelectedUC present)")
    ap.add_argument("--output", required=True, help="Output .puml file path")
    args = ap.parse_args()

    df = pd.read_csv(args.input)

    groups = defaultdict(list)
    for _, r in df.iterrows():
        cls = str(r.get('RepresentativeClassRaw') or "")
        meth = ensure_parens(str(r.get('RepresentativeMethodRaw') or ""))
        uc = str(r.get('SelectedUC') or "")
        groups[cls].append({"method": meth, "uc": uc})

    lines = []
    lines.append("@startuml")
    lines.append("hide empty members")
    lines.append("skinparam classAttributeIconSize 0")
    lines.append("skinparam ClassFontName Monospaced")
    lines.append("skinparam NoteBorderColor #BBBBBB")
    lines.append("skinparam NoteBackgroundColor #FFFFEE")

    for cls, items in sorted(groups.items(), key=lambda x: x[0].lower()):
        cls_id = sanitize_id(cls)
        lines.append(f"class \"{cls}\" as {cls_id} {{")
        for it in sorted(items, key=lambda z: z['method'].lower()):
            m = it['method']
            uc = it['uc'] if it['uc'] not in [None, "None", "nan"] else ""
            # Inline UC tag immediately after method in braces; bold red.
            # Note: PlantUML does not fully support HTML markup inside members for all themes;
            # the <b><color:red>...</color></b> markup will render in most outputs.
            suffix = f" {{<b><color:red>{uc}</color></b>}}" if uc else ""
            lines.append(f"  + {m}{suffix}")
        lines.append("}")

    lines.append("@enduml")
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    main()
