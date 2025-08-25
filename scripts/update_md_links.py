#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDES = {REPO_ROOT / 'src', REPO_ROOT / '.git', REPO_ROOT / '.pytest_cache', REPO_ROOT / '.venv', REPO_ROOT / 'venv', REPO_ROOT / 'node_modules'}

link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

def is_excluded(p: Path) -> bool:
    for ex in EXCLUDES:
        try:
            p.relative_to(ex)
            return True
        except ValueError:
            continue
    return False

# Normalize a basename (strip timestamp prefix and non-alnum to underscores, lowercase)
def norm_key(name: str) -> str:
    name = name.lower()
    if name.endswith('.md'):
        name = name[:-3]
    # strip leading timestamp like 20250818_023500_ or 20250818-023500-
    name = re.sub(r'^\d{8}[_-]?\d{6}[_-]*', '', name)
    # strip leading numbers+
    name = re.sub(r'^[0-9]+[_-]*', '', name)
    name = re.sub(r'[^a-z0-9]+', '_', name).strip('_')
    return name

# Build map from normalized key -> list of paths
md_map = {}
md_files = []
for root, dirs, files in os.walk(REPO_ROOT):
    root_p = Path(root)
    # prune excluded dirs
    dirs[:] = [d for d in dirs if not is_excluded(root_p / d)]
    for f in files:
        p = root_p / f
        if p.suffix.lower() == '.md' and not is_excluded(p):
            md_files.append(p)
            key = norm_key(p.name)
            md_map.setdefault(key, []).append(p)

# Fixed moved-file mapping (non-.md targets)
fixed_map = {
    'dashboard_app.py': 'archive/legacy_code/dashboard_app.py',
    'run_bidding_extraction_pipeline.py': 'scripts/run_bidding_extraction_pipeline.py',
    'hungerhub_sankey_diagram.html': 'docs/artifacts/hungerhub_sankey_diagram.html',
}

changed = []
for md in md_files:
    rel_base = md.parent
    text = md.read_text(encoding='utf-8', errors='ignore')
    new_text = text

    def repl(m):
        label, url = m.group(1), m.group(2)
        # Keep external links or anchors-only
        if re.match(r'^[a-zA-Z]+://', url) or url.startswith('#'):
            return m.group(0)
        # Separate fragment
        if '#' in url:
            path_part, frag = url.split('#', 1)
            frag = '#' + frag
        else:
            path_part, frag = url, ''
        # Normalize and attempt resolution
        target = (rel_base / path_part).resolve()
        if target.exists():
            return f'[{label}]({path_part})'  # leave as-is
        # Fixed map for known moves
        base_name = os.path.basename(path_part)
        if base_name in fixed_map:
            new_rel = os.path.relpath(REPO_ROOT / fixed_map[base_name], rel_base)
            return f'[{label}]({new_rel}{frag})'
        # For .md targets: try normalized key lookup
        if base_name.lower().endswith('.md'):
            key = norm_key(base_name)
            candidates = md_map.get(key, [])
            if len(candidates) == 1:
                new_rel = os.path.relpath(candidates[0], rel_base)
                return f'[{label}]({new_rel}{frag})'
        return m.group(0)

    new_text2 = link_pattern.sub(repl, new_text)
    if new_text2 != text:
        md.write_text(new_text2, encoding='utf-8')
        changed.append(str(md.relative_to(REPO_ROOT)))

print(f"Updated {len(changed)} markdown files with link fixes.")
for c in changed:
    print(f" - {c}")

