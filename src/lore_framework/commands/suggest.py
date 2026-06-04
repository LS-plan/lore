"""lore suggest — recommend experiences using FHQ-Treap + hybrid retrieval."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR
from lore_framework.engine import suggest, is_enabled


def cmd_suggest(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    if not is_enabled(lore_path):
        print("Lore is turned off. Use 'lore turnon' to re-enable.")
        return 0

    results = suggest(lore_path, args.task, count=args.count)

    if not results:
        print("No experiences found.")
        return 0

    print(f"Task: {args.task}")
    print(f"Top {len(results)} suggestions (FHQ-Treap + keyword hybrid):\n")
    print(f"  {'#':>2}  {'ID':<30s}  {'Score':>6s}  {'Rel':>5s}  {'Final':>6s}  {'Layer':<4s}  {'Impact':<8s}  Note")
    print(f"  {'—'*2}  {'—'*30}  {'—'*6}  {'—'*5}  {'—'*6}  {'—'*4}  {'—'*8}  {'—'*12}")

    for i, r in enumerate(results, 1):
        note = ""
        if r.get("mutation"):
            note = "⚡ mutation recall"
        elif r["status"] == "stale":
            note = "⏳ stale"

        triggers_str = ", ".join(r["triggers"][:2]) if r["triggers"] else "—"
        if len(r["triggers"]) > 2:
            triggers_str += f" (+{len(r['triggers']) - 2})"

        print(
            f"  {i:>2}  {r['id']:<30s}  {r['treap_score']:>6.2f}  "
            f"{r['relevance']:>5.3f}  {r['final_score']:>6.3f}  "
            f"{r['layer']:<4s}  {r['impact']:<8s}  {note}"
        )

    print(f"\n  Triggers preview:")
    for r in results[:3]:
        if r["triggers"]:
            print(f"    {r['id']}: {', '.join(r['triggers'][:3])}")

    return 0
