"""lore stats — show experience statistics with layer distribution."""

import argparse
from datetime import datetime
from pathlib import Path

from lore_framework.constants import LORE_DIR
from lore_framework.engine import (
    load_experiences,
    load_state,
    compute_score,
    layer_of,
    is_enabled,
)


def cmd_stats(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    sections = {
        "experiences": lore_path / "experiences",
        "patterns": lore_path / "patterns",
        "decisions": lore_path / "decisions",
        "domain": lore_path / "domain",
        "runs": lore_path / "runs",
    }

    print("Lore Statistics")
    print("=" * 50)

    version_file = lore_path / ".version"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    print(f"  Version:  {version}")

    enabled = is_enabled(lore_path)
    print(f"  Status:   {'ON' if enabled else 'OFF (lore turnon to re-enable)'}")

    identity = lore_path / "identity.md"
    if identity.exists():
        content = identity.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "**Project**" in line:
                print(f"  Project:  {line.split(':', 1)[-1].strip()}")
            if "**Current phase**" in line:
                raw = line.split(":", 1)[-1].strip()
                phase = raw.split("<!--")[0].strip() if "<!--" in raw else raw
                print(f"  Phase:    {phase}")

    print()

    for name, path in sections.items():
        if path.exists():
            md_files = [f for f in path.glob("*.md") if f.name != "INDEX.md"]
            yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
            total = len(md_files) + len(yaml_files)
            print(f"  {name:15s}  {total:3d} items")
        else:
            print(f"  {name:15s}  (missing)")

    # Layer distribution for experiences
    exps = load_experiences(lore_path)
    if exps:
        state = load_state(lore_path)
        today = datetime.now()
        layers = {"L1": 0, "L2": 0, "L3": 0}
        statuses = {"active": 0, "stale": 0, "archived": 0}

        for exp in exps:
            s = compute_score(exp, state, today)
            layers[layer_of(s)] += 1
            st = exp.get("status", "active")
            statuses[st] = statuses.get(st, 0) + 1

        print(f"\n  FHQ-Treap Layer Distribution:")
        print(f"    L1 (hot):   {layers['L1']:3d}")
        print(f"    L2 (warm):  {layers['L2']:3d}")
        print(f"    L3 (cold):  {layers['L3']:3d}")

        print(f"\n  Status:")
        for st, cnt in statuses.items():
            if cnt:
                print(f"    {st:12s}  {cnt:3d}")

    return 0
