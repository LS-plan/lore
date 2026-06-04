"""lore init — initialize .lore/ in the current project."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR, DIRS, GITKEEP_DIRS, TEMPLATE_VERSION
from lore_framework.templates import load_all_templates
from lore_framework.commands.inject import inject_adapters, create_and_inject
from lore_framework.registry import register_project


def cmd_init(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR

    if lore_path.exists():
        print(f"Error: {LORE_DIR}/ already exists. Use 'lore update' to upgrade.")
        return 1

    project_name = args.project or Path.cwd().name
    phase = args.phase

    print(f"Initializing Lore in {Path.cwd()}...")
    print(f"  Project: {project_name}")
    print(f"  Phase:   {phase}")

    # Create directories
    for d in DIRS:
        (lore_path / d).mkdir(parents=True, exist_ok=True)

    # Write template files
    templates = load_all_templates()
    for rel_path, content in templates.items():
        target = lore_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if rel_path in ("identity.md", "INDEX.md"):
            content = content.replace("[project name]", project_name)
        if rel_path == "identity.md":
            content = content.replace(
                "exploration  <!-- or: development -->",
                f"{phase}  <!-- or: {'development' if phase == 'exploration' else 'exploration'} -->",
            )

        target.write_text(content, encoding="utf-8")

    # Create .gitkeep files
    for d in GITKEEP_DIRS:
        (lore_path / d / ".gitkeep").touch()

    # Write version file
    (lore_path / ".version").write_text(TEMPLATE_VERSION, encoding="utf-8")

    file_count = sum(1 for _ in lore_path.rglob("*") if _.is_file())
    print(f"\nDone! Lore initialized at {LORE_DIR}/ ({file_count} files)")

    # Auto-inject adapter into detected platform config
    print("\nDetecting platform config files...")
    injected = inject_adapters(Path.cwd())

    if injected == 0:
        platform = getattr(args, "platform", None)
        injected = create_and_inject(Path.cwd(), project_name, platform=platform)
    else:
        print(f"\nAdapter auto-injected into {injected} config file(s).")

    # Register in global ~/.lore/registry.json
    register_project(str(Path.cwd()), project_name, phase)
    print(f"  Registered in ~/.lore/registry.json")

    print(f"\nStart working — your agent reads {LORE_DIR}/INDEX.md on each session.")
    return 0
