"""lore suggest — recommend experiences for a task using FHQ-Treap scheduling."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR


def cmd_suggest(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    index_path = lore_path / "experiences" / "INDEX.md"
    if not index_path.exists():
        print("No experiences found. The experience index is empty.")
        return 0

    # TODO: Parse INDEX.md, build FHQ-Treap, match triggers, suggest top-K + mutation
    print(f"Task: {args.task}")
    print(f"Requested: {args.count} suggestions")
    print()
    print("(Experience scheduling with FHQ-Treap is planned for v0.3)")
    print("For now, read .lore/experiences/INDEX.md manually.")
    return 0
