#!/usr/bin/env python3
"""Scan all specification *.txt files under docs/specs (including nested camboai mirrors)
and extract candidate module / feature names for consolidation.

Outputs:
  spec_txt_inventory.csv  - list of unique files (by content hash) with original paths
  spec_features_summary.json - extracted feature candidates with frequencies and source files

Heuristics for feature names:
  - Lines starting with emoji or bullet then text (📊, 🧠, 🎯, etc.)
  - Lines containing keywords: Engine, Panel, Hub, Generator, Lab, Room, Map, Monitor, Adapter, Center, Builder, Analyzer, Journal, Replay, Radar, Forecast
  - Table-like lines with tabs (\t) where first cell looks like a title

Duplicates: If multiple files share identical SHA256 content, only one content instance recorded; all paths listed.
"""
from __future__ import annotations
import os, pathlib, hashlib, csv, json, re, sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SEARCH_ROOTS = [REPO_ROOT / 'docs' / 'specs', REPO_ROOT / 'camboai' / 'camboai' / 'docs' / 'specs']
OUT_CSV = REPO_ROOT / 'spec_txt_inventory.csv'
OUT_JSON = REPO_ROOT / 'spec_features_summary.json'

EMOJI_START = re.compile(r'^[\s>*-]*[\W_]*[\u2190-\u2BFF\U0001F300-\U0001FAFF]')  # broad symbols range
KEYWORDS = re.compile(r'\b(Engine|Panel|Hub|Generator|Lab|Room|Map|Monitor|Adapter|Center|Builder|Analyzer|Journal|Replay|Radar|Forecast|Scanner|Strategy|Broker|Sentiment|Options)\b', re.IGNORECASE)
TRIM_PUNCT = re.compile(r'^[\s>*#\-\d\.)]+|[\s:;,.!?`]+$')

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def discover_txt() -> list[pathlib.Path]:
    files = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.lower().endswith('.txt'):
                    files.append(pathlib.Path(dirpath) / fn)
    return files

def extract_features(lines: list[str]) -> list[str]:
    feats = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        candidate = None
        tabbed = '\t' in line
        if EMOJI_START.search(line) or KEYWORDS.search(line) or tabbed:
            # Take up to first 120 chars
            candidate = line[:120]
            # Remove trailing explanatory clause after two dashes
            # Clean punctuation around
            candidate = TRIM_PUNCT.sub('', candidate)
            # Avoid giant paragraphs (skip if > 12 words w/o keyword emphasis)
            if len(candidate.split()) > 16 and not KEYWORDS.search(candidate):
                continue
        if candidate:
            # Normalize multiple spaces
            candidate = re.sub(r'\s{2,}', ' ', candidate)
            # Collapse emoji + space
            feats.append(candidate)
    return feats

def main():
    txt_files = discover_txt()
    content_map: dict[str, dict] = {}
    for p in txt_files:
        try:
            h = sha256(p)
            rec = content_map.setdefault(h, {"hash": h, "paths": [], "features": []})
            rec["paths"].append(str(p.relative_to(REPO_ROOT)))
            if not rec["features"]:  # parse once per unique content
                try:
                    with p.open('r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    feats = extract_features(lines)
                    rec["features"] = feats
                except Exception as e:
                    rec["features"] = [f"__PARSE_ERROR__: {e}"]
        except Exception:
            continue

    # Aggregate feature frequencies
    freq: dict[str, dict] = {}
    for rec in content_map.values():
        for feat in rec["features"]:
            if feat.startswith('__PARSE_ERROR__'):
                continue
            fentry = freq.setdefault(feat, {"count": 0, "hashes": set(), "paths": set()})
            fentry["count"] += 1
            fentry["hashes"].add(rec["hash"])
            for p in rec["paths"]:
                fentry["paths"].add(p)

    # Write inventory CSV
    with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['hash', 'num_paths', 'sample_path'])
        for h, rec in sorted(content_map.items(), key=lambda x: x[0]):
            w.writerow([h, len(rec['paths']), rec['paths'][0]])

    # Prepare JSON summary
    feature_list = []
    for feat, meta in sorted(freq.items(), key=lambda x: (-x[1]['count'], x[0].lower())):
        feature_list.append({
            'feature': feat,
            'occurrences': meta['count'],
            'file_count': len(meta['paths']),
            'example_paths': sorted(list(meta['paths']))[:5]
        })

    OUT_JSON.write_text(json.dumps({
        'total_txt_files': len(txt_files),
        'unique_content_blobs': len(content_map),
        'features_extracted': len(feature_list),
        'features': feature_list
    }, indent=2), encoding='utf-8')

    print(f"Scanned {len(txt_files)} txt files. Unique content: {len(content_map)}. Features: {len(feature_list)}.")
    print(f"Inventory: {OUT_CSV.relative_to(REPO_ROOT)}  Summary: {OUT_JSON.relative_to(REPO_ROOT)}")

if __name__ == '__main__':
    main()
