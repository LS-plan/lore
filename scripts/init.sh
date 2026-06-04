#!/usr/bin/env bash
set -euo pipefail

LORE_DIR=".lore"
REPO_URL="https://raw.githubusercontent.com/LS-plan/lore/main/template/.lore"

if [ -d "$LORE_DIR" ]; then
  echo "Error: $LORE_DIR already exists in this directory."
  echo "If you want to reinitialize, remove it first: rm -rf $LORE_DIR"
  exit 1
fi

echo "Initializing Lore in $(pwd)..."

mkdir -p "$LORE_DIR"/{domain,experiences,decisions,patterns,runs,_adapters}

# Download template files
files=(
  "INDEX.md"
  "identity.md"
  "glossary.md"
  "domain/INDEX.md"
  "experiences/INDEX.md"
  "patterns/INDEX.md"
  "_adapters/claude-code.md"
  "_adapters/codex.md"
  "_adapters/cursor.md"
  "_adapters/gemini.md"
)

for f in "${files[@]}"; do
  curl -fsSL "$REPO_URL/$f" -o "$LORE_DIR/$f" 2>/dev/null || {
    echo "Warning: Could not download $f (offline? private repo?)"
    echo "You can copy templates manually from https://github.com/LS-plan/lore"
  }
done

touch "$LORE_DIR/runs/.gitkeep"
touch "$LORE_DIR/decisions/.gitkeep"

echo ""
echo "Done! Lore initialized at $LORE_DIR/"
echo ""
echo "Next steps:"
echo "  1. Edit $LORE_DIR/identity.md to describe your project"
echo "  2. Copy the adapter snippet from $LORE_DIR/_adapters/ into your platform config"
echo "     (e.g., CLAUDE.md for Claude Code, AGENTS.md for Codex)"
echo "  3. Start working — your agent will read $LORE_DIR/INDEX.md on each session"
