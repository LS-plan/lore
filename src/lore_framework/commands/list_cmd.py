"""lore list — list all registered Lore projects."""

import argparse

from lore_framework.registry import list_projects, get_global_stats


def cmd_list(args: argparse.Namespace) -> int:
    if args.global_stats:
        return _show_global_stats()
    return _show_project_list()


def _show_project_list() -> int:
    projects = list_projects()
    if not projects:
        print("No projects registered. Run 'lore init' in a project directory.")
        return 0

    print(f"Registered Lore Projects ({len(projects)})")
    print("=" * 70)
    print(f"  {'#':>2}  {'Name':<20s}  {'Phase':<12s}  {'Last Active':<16s}  Path")
    print(f"  {'—'*2}  {'—'*20}  {'—'*12}  {'—'*16}  {'—'*20}")

    for i, p in enumerate(projects, 1):
        print(
            f"  {i:>2}  {p['name']:<20s}  {p.get('phase', '?'):<12s}  "
            f"{p.get('last_active', '—'):<16s}  {p['path']}"
        )

    return 0


def _show_global_stats() -> int:
    stats = get_global_stats()

    print("Global Lore Statistics")
    print("=" * 60)
    print(f"  Projects:     {stats['projects']}")
    print(f"  Experiences:  {stats['total_experiences']}")
    print(f"  Patterns:     {stats['total_patterns']}")

    if stats["total_experiences"]:
        print(f"\n  FHQ-Treap Layer Distribution (all projects):")
        print(f"    L1 (hot):   {stats['layers']['L1']}")
        print(f"    L2 (warm):  {stats['layers']['L2']}")
        print(f"    L3 (cold):  {stats['layers']['L3']}")

    if stats["per_project"]:
        print(f"\n  Per Project:")
        print(f"    {'Name':<20s}  {'Exp':>4s}  {'Pat':>4s}  {'L1':>3s}  {'L2':>3s}  {'L3':>3s}  {'Phase':<12s}")
        print(f"    {'—'*20}  {'—'*4}  {'—'*4}  {'—'*3}  {'—'*3}  {'—'*3}  {'—'*12}")
        for p in stats["per_project"]:
            if p.get("status") == "missing":
                print(f"    {p['name']:<20s}  (directory missing)")
                continue
            layers = p.get("layers", {})
            print(
                f"    {p['name']:<20s}  {p['experiences']:>4d}  {p['patterns']:>4d}  "
                f"{layers.get('L1', 0):>3d}  {layers.get('L2', 0):>3d}  {layers.get('L3', 0):>3d}  "
                f"{p.get('phase', '?'):<12s}"
            )

    return 0
