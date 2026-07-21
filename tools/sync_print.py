#!/usr/bin/env python3
"""Sync built artifacts (*.stl / *.pdf) from their model sources into the
per-version print/ folders.

The print/ trees (v2/print, v2.1/print, v3/print) hold hand-copied duplicates
of files that are actually *built* under a model source dir (models/,
v2/models, v3/models, ...). After rebuilding a part it is easy to forget to
refresh those copies, so they silently drift. This script re-copies every
print file from its authoritative source, matched by file name.

Usage:
    python tools/sync_print.py            # sync: copy sources over stale prints
    python tools/sync_print.py --dry-run  # show what would change, copy nothing
    python tools/sync_print.py --check    # exit 1 if anything is out of sync
                                          #   (no writes) — for pre-commit / CI

A source is located by matching the print file's *base name* anywhere in the
source tree. Base names are unique across sources (the script verifies this and
aborts on any collision). Print files with no matching source (e.g. assembly
bundles built elsewhere) are reported and skipped, never guessed.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

# Repo root = pov3d/ (parent of this tools/ dir)
ROOT = Path(__file__).resolve().parent.parent

# Extensions treated as build artifacts to keep in sync.
ARTIFACT_EXTS = {".stl", ".pdf"}

# Directories that never contain authoritative sources.
EXCLUDE_DIR_NAMES = {".venv", ".git", "__pycache__", "print"}


def _iter_files(base: Path):
    """Yield artifact files under base, skipping excluded directories."""
    for p in base.rglob("*"):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in p.relative_to(ROOT).parts):
            continue
        if p.suffix.lower() in ARTIFACT_EXTS:
            yield p


def build_source_index():
    """Map artifact base name -> source Path. Abort on any name collision."""
    index = {}
    collisions = {}
    for p in _iter_files(ROOT):
        index.setdefault(p.name, [])
        index[p.name].append(p)
    for name, paths in index.items():
        if len(paths) > 1:
            collisions[name] = paths
    if collisions:
        print("ERROR: ambiguous source file names (cannot sync safely):",
              file=sys.stderr)
        for name, paths in sorted(collisions.items()):
            print(f"  {name}:", file=sys.stderr)
            for pth in paths:
                print(f"    {pth.relative_to(ROOT)}", file=sys.stderr)
        sys.exit(2)
    return {name: paths[0] for name, paths in index.items()}


def find_print_files():
    """All artifact files living under any print/ directory."""
    out = []
    for print_dir in sorted(ROOT.glob("*/print")):
        for p in print_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in ARTIFACT_EXTS:
                out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true",
                   help="show what would change without copying")
    g.add_argument("--check", action="store_true",
                   help="exit 1 if any print copy is out of sync (no writes)")
    args = ap.parse_args()

    sources = build_source_index()
    print_files = find_print_files()

    updated, up_to_date, no_source = [], 0, []

    for dst in print_files:
        src = sources.get(dst.name)
        if src is None:
            no_source.append(dst)
            continue
        if filecmp.cmp(src, dst, shallow=False):
            up_to_date += 1
            continue
        updated.append((src, dst))
        if not (args.dry_run or args.check):
            shutil.copy2(src, dst)

    # ---- Report ----
    rel = lambda p: p.relative_to(ROOT)
    verb = "would update" if (args.dry_run or args.check) else "updated"
    for src, dst in updated:
        print(f"  {verb}: {rel(dst)}  <-  {rel(src)}")
    for dst in no_source:
        print(f"  no source (skipped): {rel(dst)}")

    print(f"\n{len(print_files)} print files: "
          f"{up_to_date} in sync, {len(updated)} {verb}, "
          f"{len(no_source)} without source.")

    if args.check and updated:
        print("\nFAIL: print copies are out of sync. "
              "Run `python tools/sync_print.py` to fix.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
