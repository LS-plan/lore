"""lore gc — clean up stale runs and archive expired experiences."""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from lore_framework.constants import LORE_DIR

RUNS_MAX_AGE_DAYS = 30


def cmd_gc(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    runs_dir = lore_path / "runs"
    cutoff = datetime.now() - timedelta(days=RUNS_MAX_AGE_DAYS)
    cleaned = 0

    if runs_dir.exists():
        for f in runs_dir.iterdir():
            if f.name == ".gitkeep":
                continue
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                if args.dry_run:
                    print(f"  [remove] {LORE_DIR}/runs/{f.name} (older than {RUNS_MAX_AGE_DAYS} days)")
                else:
                    f.unlink()
                    print(f"  [removed] {LORE_DIR}/runs/{f.name}")
                cleaned += 1

    # TODO: Scan experiences/ for stale → archived transitions

    if cleaned == 0:
        print("Nothing to clean up.")
    else:
        action = "Would remove" if args.dry_run else "Removed"
        print(f"\n{action} {cleaned} stale run(s).")

    if args.dry_run:
        print("(dry run — no files were changed)")

    return 0
