#!/usr/bin/env python3
"""Consolidate duplicated module files across the repo.

Usage: python scripts/consolidate_modules.py --dry-run

Logic:
- Target basenames: chart_module.py, education_module.py, strategy_engine.py, sentiment_panel.py, launch.py
- Search all paths excluding: venv, env, .venv, __pycache__, node_modules, archive, .git
- Group by basename, compute SHA256 hash.
- Canonical priority order roots (first match kept):
    1. modules/
    2. modules/strategy/
    3. modules/panels/
    4. backend/app/**
    5. camboai/backend/app/**
    6. (others, including docs/specs) treated as archival
- For each group:
    * If identical hashes to canonical -> ignore
    * If different -> copy to archive/snapshots/<basename>__variantN.py
- Emit consolidation_manifest.json summarizing actions.
"""
from __future__ import annotations
import hashlib, json, os, shutil, argparse, pathlib, sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE_DIR = REPO_ROOT / 'archive' / 'snapshots'
TARGET_BASENAMES = {
    'chart_module.py', 'education_module.py', 'strategy_engine.py', 'sentiment_panel.py', 'launch.py'
}
EXCLUDE_PARTS = {'.git', 'venv', '.venv', 'env', '__pycache__', 'node_modules', 'archive'}
PRIORITY_SUBSTR = [
    'modules\\', 'modules/strategy', 'modules/panels', 'backend/app', 'camboai/backend/app'
]

manifest = {"files": []}

def is_excluded(path: pathlib.Path) -> bool:
    parts = set(path.parts)
    return any(p in EXCLUDE_PARTS for p in parts)

def priority_key(p: pathlib.Path) -> int:
    s = str(p).replace(os.sep, '/')
    for i, sub in enumerate(PRIORITY_SUBSTR):
        if sub in s:
            return i
    return len(PRIORITY_SUBSTR)

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def find_targets():
    groups = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        # prune dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_PARTS]
        for f in files:
            if f in TARGET_BASENAMES:
                path = pathlib.Path(root) / f
                if is_excluded(path):
                    continue
                groups.setdefault(f, []).append(path)
    return groups

def consolidate(dry_run: bool = True):
    groups = find_targets()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for basename, paths in groups.items():
        paths_sorted = sorted(paths, key=priority_key)
        canonical = paths_sorted[0]
        canonical_hash = sha256(canonical)
        variant_index = 1
        for p in paths_sorted[1:]:
            h = sha256(p)
            entry = {"basename": basename, "path": str(p), "hash": h, "action": None}
            if h == canonical_hash:
                entry["action"] = "duplicate_same_hash_skipped"
            else:
                # archive variant
                target = ARCHIVE_DIR / f"{basename}__variant{variant_index}.py"
                variant_index += 1
                entry["action"] = "archived_variant" if not dry_run else "would_archive_variant"
                if not dry_run:
                    shutil.copy2(p, target)
                    entry["archived_to"] = str(target)
            manifest["files"].append(entry)
        manifest["files"].append({
            "basename": basename,
            "path": str(canonical),
            "hash": canonical_hash,
            "action": "canonical"
        })
    out = REPO_ROOT / 'consolidation_manifest.json'
    out.write_text(json.dumps(manifest, indent=2))
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Perform archival (default dry-run).')
    args = parser.parse_args()
    out_path = consolidate(dry_run=not args.apply)
    print(f"Manifest written to {out_path} (apply={args.apply})")
