"""lore inject — auto-detect platform and inject adapter snippet."""

import argparse
import os
import re
import shutil
from pathlib import Path

from lore_framework.constants import LORE_DIR
from lore_framework.templates import TEMPLATES

PLATFORM_CONFIGS = [
    ("CLAUDE.md", "_adapters/claude-code.md", "Claude Code"),
    ("AGENTS.md", "_adapters/codex.md", "Codex"),
    (".cursorrules", "_adapters/cursor.md", "Cursor"),
    (".cursor/rules", "_adapters/cursor.md", "Cursor"),
    (".gemini/settings.json", "_adapters/gemini.md", "Gemini"),
]

MARKER = "## Project Experience (Lore)"


def detect_platform() -> tuple[str, str, str]:
    """Auto-detect the current AI coding platform.

    Returns (config_filename, adapter_key, platform_name).
    Priority: env-var match (strongest signal) → command existence → default.
    """
    # Cursor IDE: env vars are the strongest signal for "running inside Cursor"
    if os.environ.get("CURSOR_CHANNEL") or "cursor" in os.environ.get("TERM_PROGRAM", "").lower():
        return ".cursorrules", "_adapters/cursor.md", "Cursor"

    # Gemini: Google AI environment indicators
    if os.environ.get("GEMINI_API_KEY"):
        return ".gemini/settings.json", "_adapters/gemini.md", "Gemini"

    # Claude Code: CLAUDE_* env vars = running inside Claude Code right now
    if any(k.startswith("CLAUDE_") for k in os.environ):
        return "CLAUDE.md", "_adapters/claude-code.md", "Claude Code"

    # Codex: CODEX_HOME env var = running inside Codex right now
    if os.environ.get("CODEX_HOME"):
        return "AGENTS.md", "_adapters/codex.md", "Codex"

    # Fallback: check installed commands (weaker signal — tool installed but maybe not active)
    if shutil.which("claude"):
        return "CLAUDE.md", "_adapters/claude-code.md", "Claude Code"
    if shutil.which("codex"):
        return "AGENTS.md", "_adapters/codex.md", "Codex"

    return "CLAUDE.md", "_adapters/claude-code.md", "Claude Code"


def _extract_snippet(adapter_template: str) -> str:
    """Extract the injectable snippet from an adapter template."""
    lines = adapter_template.splitlines()
    in_fence = False
    snippet_lines = []

    for line in lines:
        if not in_fence and re.match(r"^```", line):
            in_fence = True
            continue
        if in_fence and line.strip() == "```":
            break
        if in_fence:
            snippet_lines.append(line)

    return "\n".join(snippet_lines).strip()


def inject_adapters(project_root: Path, quiet: bool = False) -> int:
    """Detect platform configs and inject Lore adapter snippets. Returns count injected."""
    injected = 0

    for config_rel, adapter_key, platform_name in PLATFORM_CONFIGS:
        config_path = project_root / config_rel
        if not config_path.exists():
            continue

        adapter_template = TEMPLATES.get(adapter_key)
        if not adapter_template:
            continue

        snippet = _extract_snippet(adapter_template)
        if not snippet:
            continue

        existing = config_path.read_text(encoding="utf-8")
        if MARKER in existing:
            if not quiet:
                print(f"  [skip] {config_rel} — Lore adapter already present")
            continue

        separator = "\n\n" if existing.strip() else ""
        config_path.write_text(existing + separator + snippet + "\n", encoding="utf-8")
        injected += 1
        if not quiet:
            print(f"  [injected] {config_rel} ← {platform_name} adapter")

    return injected


def create_and_inject(project_root: Path, project_name: str, platform: str | None = None) -> int:
    """Create the platform config file and inject the Lore adapter.

    If platform is None, auto-detect. Returns count injected.
    """
    if platform:
        match = [(c, a, p) for c, a, p in PLATFORM_CONFIGS if p.lower() == platform.lower()]
        if not match:
            print(f"  Unknown platform: {platform}")
            print(f"  Supported: {', '.join(p for _, _, p in PLATFORM_CONFIGS)}")
            return 0
        config_rel, adapter_key, platform_name = match[0]
    else:
        config_rel, adapter_key, platform_name = detect_platform()

    config_path = project_root / config_rel
    print(f"  Detected platform: {platform_name} → creating {config_rel}")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.write_text(f"# {project_name}\n", encoding="utf-8")

    adapter_template = TEMPLATES.get(adapter_key)
    if not adapter_template:
        return 0

    snippet = _extract_snippet(adapter_template)
    if not snippet:
        return 0

    existing = config_path.read_text(encoding="utf-8")
    if MARKER in existing:
        print(f"  [skip] {config_rel} — Lore adapter already present")
        return 0

    separator = "\n\n" if existing.strip() else ""
    config_path.write_text(existing + separator + snippet + "\n", encoding="utf-8")
    print(f"  [injected] {config_rel} ← {platform_name} adapter")
    return 1


def refresh_adapters(project_root: Path) -> int:
    """Replace existing Lore adapter snippets with the latest version. Returns count refreshed."""
    refreshed = 0

    for config_rel, adapter_key, platform_name in PLATFORM_CONFIGS:
        config_path = project_root / config_rel
        if not config_path.exists():
            continue

        existing = config_path.read_text(encoding="utf-8")
        if MARKER not in existing:
            continue

        adapter_template = TEMPLATES.get(adapter_key)
        if not adapter_template:
            continue

        new_snippet = _extract_snippet(adapter_template)
        if not new_snippet:
            continue

        idx = existing.index(MARKER)
        before = existing[:idx].rstrip()

        after_marker = existing[idx + len(MARKER):]
        lines_after = after_marker.split("\n")
        end_offset = len(after_marker)
        for i, line in enumerate(lines_after):
            if i == 0:
                continue
            if line.startswith("## ") and "Lore" not in line:
                end_offset = sum(len(l) + 1 for l in lines_after[:i])
                break

        rest = after_marker[end_offset:]
        separator = "\n\n" if before.strip() else ""
        new_content = before + separator + new_snippet + "\n" + rest
        config_path.write_text(new_content, encoding="utf-8")
        refreshed += 1
        print(f"  [refreshed] {config_rel} ← {platform_name} adapter (updated to latest)")

    return refreshed


def cmd_inject(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR
    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    print("Detecting platform config files...")
    count = inject_adapters(Path.cwd())

    if count == 0:
        existing_configs = any(
            (Path.cwd() / c).exists() for c, _, _ in PLATFORM_CONFIGS
        )
        if existing_configs:
            print("All detected configs already have Lore adapter.")
        else:
            print("No platform config files found. Creating one...")
            project_name = Path.cwd().name
            count = create_and_inject(Path.cwd(), project_name)

    if count:
        print(f"\nInjected Lore adapter into {count} config file(s).")

    return 0
