
import re
import pandas as pd
from collections import defaultdict

def canon(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def read_annotations(path: str) -> pd.DataFrame:
    """
    Robust reader for the annotations CSV (semicolon-separated, Win-1252 in this dataset).
    """
    try:
        df = pd.read_csv(path, sep=';', encoding='Windows-1252')
    except Exception:
        df = pd.read_csv(path, sep=';', encoding='utf-8', engine='python')
    # normalize columns
    rename_map = {
        'Class': 'Class',
        'MethodName': 'MethodName',
        'Model': 'Model',
        'Run': 'Run',
        'UC_References': 'UC_References',
        'UC_Action': 'UC_Action',
        'Has_UC_Annotation': 'Has_UC_Annotation',
        'Signature': 'Signature',
        'File': 'File'
    }
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    # Canonical forms
    df['class_canon'] = df['Class'].apply(canon)
    df['method_canon'] = df['MethodName'].apply(canon)
    df['pair'] = list(zip(df['class_canon'], df['method_canon']))
    # Normalize UC tag
    def uc_norm(x):
        if pd.isna(x):
            return None
        try:
            # Handles floats like 19.0
            n = int(float(x))
            return f"UC{n:02d}"
        except Exception:
            # Try to parse strings like "UC19" or "19, 20"
            s = str(x).strip()
            if s.upper().startswith("UC"):
                try:
                    n = int(re.sub(r'[^0-9]', '', s))
                    return f"UC{n:02d}"
                except Exception:
                    return None
            # fallback: pick first integer
            m = re.search(r'\d+', s)
            if m:
                return f"UC{int(m.group(0)):02d}"
            return None
    df['UC_tag'] = df['UC_References'].apply(uc_norm)
    # normalize Has_UC_Annotation to bool
    df['Has_UC_Annotation_norm'] = df['Has_UC_Annotation'].astype(str).str.strip().str.upper().isin(['TRUE','VRAI','1','YES','OUI'])
    return df

def distinct_model_support(df: pd.DataFrame):
    """
    Returns a DataFrame with columns: pair, support_models (distinct models count)
    """
    model_pair = df.groupby(['Model','pair']).size().reset_index(name='n')
    support = model_pair.groupby('pair')['Model'].nunique().reset_index(name='support_models')
    return support

def uc_support_for_pair(df: pd.DataFrame, pair):
    """
    For a given canonical pair, compute:
    - distinct-model support per UC
    - instance counts per UC
    Returns dict: uc -> {'models': int, 'instances': int}
    """
    sub = df[df['pair']==pair].copy()
    # consider rows that have a UC tag at all
    sub_with_uc = sub[~sub['UC_tag'].isna()].copy()
    result = {}
    if sub_with_uc.empty:
        return result
    # Distinct models per (UC, pair)
    mp = sub_with_uc.groupby(['UC_tag','Model']).size().reset_index(name='n')
    model_counts = mp.groupby('UC_tag')['Model'].nunique().to_dict()
    inst_counts = sub_with_uc.groupby('UC_tag').size().to_dict()
    for uc in set(list(model_counts.keys()) + list(inst_counts.keys())):
        result[uc] = {'models': int(model_counts.get(uc, 0)), 'instances': int(inst_counts.get(uc, 0))}
    return result

def uc_select_for_pair(df: pd.DataFrame, pair, k_models=5):
    """
    Deterministic UC selection rule for a pair.
    Returns (selected_uc or None, selection_mode: 'consensus' or 'fallback' or 'none')
    """
    votes = uc_support_for_pair(df, pair)
    if not votes:
        return (None, 'none')
    # consensus set
    consensus = [ (uc, v['models'], v['instances']) for uc, v in votes.items() if v['models'] >= k_models ]
    if consensus:
        # choose by higher model support, then higher instances, then smaller numeric UC
        consensus.sort(key=lambda x: (-x[1], -x[2], int(x[0][2:])))
        return (consensus[0][0], 'consensus')
    # fallback: highest instances; tie by higher model support; then smaller UC
    fallback = [ (uc, v['models'], v['instances']) for uc, v in votes.items() ]
    fallback.sort(key=lambda x: (-x[2], -x[1], int(x[0][2:])))
    return (fallback[0][0], 'fallback')

def representative_raw_method(df: pd.DataFrame, pair):
    sub = df[df['pair']==pair]
    if sub.empty:
        return None
    counts = sub.groupby('MethodName').size().reset_index(name='n').sort_values('n', ascending=False)
    return counts.iloc[0]['MethodName']

def representative_raw_class(df: pd.DataFrame, pair):
    sub = df[df['pair']==pair]
    if sub.empty:
        return None
    counts = sub.groupby('Class').size().reset_index(name='n').sort_values('n', ascending=False)
    return counts.iloc[0]['Class']

def collect_actions(df: pd.DataFrame, pair, top_n=5):
    sub = df[df['pair']==pair]
    if sub.empty or 'UC_Action' not in sub.columns:
        return []
    counts = sub['UC_Action'].dropna().astype(str).str.strip().str.lower().value_counts()
    items = [(a,c) for a,c in counts.head(top_n).items()]
    return items
