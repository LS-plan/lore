"""Shared constants."""

from pathlib import Path

LORE_DIR = ".lore"
VERSION_FILE = ".version"
TEMPLATE_VERSION = "0.2.0"

DIRS = [
    "domain",
    "experiences",
    "decisions",
    "patterns",
    "runs",
    "_adapters",
]

TEMPLATE_FILES = [
    "INDEX.md",
    "identity.md",
    "glossary.md",
    "domain/INDEX.md",
    "experiences/INDEX.md",
    "patterns/INDEX.md",
    "_adapters/claude-code.md",
    "_adapters/codex.md",
    "_adapters/cursor.md",
    "_adapters/gemini.md",
]

GITKEEP_DIRS = ["runs", "decisions"]


def get_template_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent / "template" / LORE_DIR
