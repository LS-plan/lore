"""lore stats — show experience statistics."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR


def cmd_stats(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    # Count files in each directory
    sections = {
        "experiences": lore_path / "experiences",
        "patterns": lore_path / "patterns",
        "decisions": lore_path / "decisions",
        "domain": lore_path / "domain",
        "runs": lore_path / "runs",
    }

    print("Lore Statistics")
    print("=" * 40)

    version_file = lore_path / ".version"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    print(f"  Version:  {version}")

    identity = lore_path / "identity.md"
    if identity.exists():
        content = identity.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "**Project**" in line:
                print(f"  Project:  {line.split(':')[-1].strip()}")
            if "**Current phase**" in line:
                raw = line.split(":")[-1].strip()
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

    return 0
