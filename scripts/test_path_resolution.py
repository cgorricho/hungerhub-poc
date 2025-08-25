#!/usr/bin/env python3
from pathlib import Path
import os
import sys

try:
    from src.utils.paths import get_data_dir, get_project_root
except Exception as e:
    print(f"ERROR: cannot import paths utils: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("[Test] Path resolution cross-CWD")
    root = get_project_root()
    print(f"Detected project root: {root}")
    unified = get_data_dir('processed/unified_real')
    real = get_data_dir('processed/real')
    print(f"unified_real path: {unified}")
    print(f"real path:        {real}")
    print(f"Exists(unified_real): {unified.exists()}")
    print(f"Exists(real):        {real.exists()}")
    # If running from src/, ensure paths still resolve under repo root/data, not src/data
    if 'src' in str(Path.cwd()) and '/data/' in str(unified):
        print("WARNING: unified path contains '/data/' while CWD has 'src' — verify it is repo root data, not src/data")

