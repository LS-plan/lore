"""lore gc — clean up stale runs, apply TTL, archive expired experiences."""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from lore_framework.constants import LORE_DIR
from lore_framework.engine import update_ttl

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

    # TTL: stale/archive experiences based on usage
    ttl_result = update_ttl(lore_path, dry_run=args.dry_run)
    ttl_count = 0

    for eid in ttl_result["stale"]:
        action = "would mark" if args.dry_run else "marked"
        print(f"  [{action}] {eid} → stale (unused {90}+ days)")
        ttl_count += 1

    for eid in ttl_result["archived"]:
        action = "would archive" if args.dry_run else "archived"
        print(f"  [{action}] {eid} → archived (unused {180}+ days)")
        ttl_count += 1

    for eid in ttl_result["exempt"]:
        print(f"  [exempt] {eid} (impact: critical, skip auto-expiry)")

    total = cleaned + ttl_count
    if total == 0:
        print("Nothing to clean up.")
    else:
        action = "Would process" if args.dry_run else "Processed"
        parts = []
        if cleaned:
            parts.append(f"{cleaned} stale run(s)")
        if ttl_count:
            parts.append(f"{ttl_count} experience TTL update(s)")
        print(f"\n{action} {', '.join(parts)}.")

    if args.dry_run:
        print("(dry run — no files were changed)")

    return 0
