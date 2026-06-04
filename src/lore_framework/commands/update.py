"""lore update — incrementally update .lore/ to the latest template version."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR, DIRS, TEMPLATE_VERSION
from lore_framework.templates import load_all_templates


def _is_user_modified(local_file: Path, template_content: str) -> bool:
    """Check if the user has modified a file from the template."""
    if not local_file.exists():
        return False
    local_content = local_file.read_text(encoding="utf-8")
    return local_content != template_content


def cmd_update(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    version_file = lore_path / ".version"
    current_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.1.0"

    if current_version == TEMPLATE_VERSION:
        print(f"Already at the latest version ({TEMPLATE_VERSION}). Nothing to update.")
        return 0

    print(f"Updating {LORE_DIR}/ from v{current_version} to v{TEMPLATE_VERSION}...")

    # Ensure all directories exist
    for d in DIRS:
        dir_path = lore_path / d
        if not dir_path.exists():
            if args.dry_run:
                print(f"  [create dir] {LORE_DIR}/{d}/")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  [created]    {LORE_DIR}/{d}/")

    templates = load_all_templates()
    added = 0
    skipped = 0
    updated = 0

    for rel_path, content in templates.items():
        target = lore_path / rel_path

        if not target.exists():
            # New file — add it
            if args.dry_run:
                print(f"  [add]    {LORE_DIR}/{rel_path}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                print(f"  [added]  {LORE_DIR}/{rel_path}")
            added += 1
        elif _is_user_modified(target, content):
            # User has modified this file — skip
            print(f"  [skip]   {LORE_DIR}/{rel_path} (user-modified)")
            skipped += 1
        else:
            # Unchanged from previous template — safe to update
            if target.read_text(encoding="utf-8") != content:
                if args.dry_run:
                    print(f"  [update] {LORE_DIR}/{rel_path}")
                else:
                    target.write_text(content, encoding="utf-8")
                    print(f"  [updated] {LORE_DIR}/{rel_path}")
                updated += 1

    # Update version file
    if not args.dry_run:
        version_file.write_text(TEMPLATE_VERSION, encoding="utf-8")

    action = "Would update" if args.dry_run else "Updated"
    print(f"\n{action}: {added} added, {updated} updated, {skipped} skipped (user-modified)")

    if args.dry_run:
        print("(dry run — no files were changed)")

    return 0
