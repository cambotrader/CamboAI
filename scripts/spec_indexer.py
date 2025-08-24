"""
Spec Indexer: scans TXT/MD files under docs/specs for ideas/modules, finds duplicates by fuzzy match,
outputs a JSON summary report and a markdown digest.
"""
import os
import re
import json
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(r"d:\CamboAI\docs\specs")
OUT_DIR = Path(r"d:\CamboAI\scripts\reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEXT_EXT = {".txt", ".md"}


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def collect_files(root: Path):
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            files.append(p)
    return files


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def summarize(text: str, max_len: int = 300) -> str:
    # crude summary: first 300 chars
    return (text[:max_len] + ("..." if len(text) > max_len else "")).replace("\n", " ")


def main():
    files = collect_files(ROOT)
    items = []
    for f in files:
        raw = read_text(f)
        items.append({
            "path": str(f),
            "size": len(raw),
            "preview": summarize(raw),
            "norm": normalize(raw)
        })

    # duplicate clusters by fuzzy threshold
    THRESH = 0.9
    visited = set()
    clusters = []

    for i in range(len(items)):
        if i in visited:
            continue
        base = items[i]
        cluster = [i]
        visited.add(i)
        for j in range(i + 1, len(items)):
            if j in visited:
                continue
            if similarity(base["norm"], items[j]["norm"]) >= THRESH:
                cluster.append(j)
                visited.add(j)
        clusters.append(cluster)

    # Build report
    report = {
        "root": str(ROOT),
        "total_files": len(items),
        "clusters": []
    }

    for cluster in clusters:
        members = [
            {
                "path": items[k]["path"],
                "size": items[k]["size"],
                "preview": items[k]["preview"]
            }
            for k in cluster
        ]
        report["clusters"].append({
            "count": len(cluster),
            "members": members
        })

    OUT_JSON = OUT_DIR / "spec_duplicates.json"
    OUT_MD = OUT_DIR / "spec_duplicates.md"

    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Markdown digest
    lines = ["# Spec Duplicate Report", "", f"Root: {ROOT}", f"Total text files: {len(items)}", ""]
    for idx, c in enumerate(report["clusters"], 1):
        if c["count"] <= 1:
            continue
        lines.append(f"## Cluster {idx} — {c['count']} similar files")
        for m in c["members"]:
            lines.append(f"- {m['path']} ({m['size']} bytes)")
            lines.append(f"  - {m['preview']}")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()