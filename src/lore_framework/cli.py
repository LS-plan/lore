"""Lore CLI entry point."""

import argparse
import sys

from lore_framework import __version__
from lore_framework.commands.init import cmd_init
from lore_framework.commands.update import cmd_update
from lore_framework.commands.stats import cmd_stats
from lore_framework.commands.suggest import cmd_suggest
from lore_framework.commands.gc import cmd_gc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lore",
        description="Lore — Project Experience Framework for AI agents.",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"lore {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    # lore init
    p_init = sub.add_parser("init", help="Initialize .lore/ in the current project")
    p_init.add_argument(
        "--project", "-p", default=None,
        help="Project name (auto-detected from directory name if omitted)",
    )
    p_init.add_argument(
        "--phase", default="exploration",
        choices=["exploration", "development"],
        help="Initial phase (default: exploration)",
    )

    # lore update
    p_update = sub.add_parser("update", help="Incrementally update .lore/ to the latest version")
    p_update.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files",
    )

    # lore suggest
    p_suggest = sub.add_parser("suggest", help="Suggest experiences for a task")
    p_suggest.add_argument("--task", "-t", required=True, help="Task description")
    p_suggest.add_argument("--count", "-n", type=int, default=5, help="Number of suggestions")

    # lore stats
    sub.add_parser("stats", help="Show experience statistics")

    # lore gc
    p_gc = sub.add_parser("gc", help="Clean up stale runs and archive expired experiences")
    p_gc.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be cleaned without modifying files",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    handlers = {
        "init": cmd_init,
        "update": cmd_update,
        "suggest": cmd_suggest,
        "stats": cmd_stats,
        "gc": cmd_gc,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
