$ErrorActionPreference = "Stop"

$LoreDir = ".lore"
$RepoUrl = "https://raw.githubusercontent.com/LS-plan/lore/main/template/.lore"

if (Test-Path $LoreDir) {
    Write-Error "$LoreDir already exists in this directory. Remove it first if you want to reinitialize."
    exit 1
}

Write-Host "Initializing Lore in $(Get-Location)..."

$dirs = @(
    "$LoreDir/domain"
    "$LoreDir/experiences"
    "$LoreDir/decisions"
    "$LoreDir/patterns"
    "$LoreDir/runs"
    "$LoreDir/_adapters"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

$files = @(
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

foreach ($f in $files) {
    try {
        Invoke-WebRequest -Uri "$RepoUrl/$f" -OutFile "$LoreDir/$f" -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Warning "Could not download $f (offline? private repo?). Copy templates manually from https://github.com/LS-plan/lore"
    }
}

New-Item -ItemType File -Force -Path "$LoreDir/runs/.gitkeep" | Out-Null
New-Item -ItemType File -Force -Path "$LoreDir/decisions/.gitkeep" | Out-Null

Write-Host ""
Write-Host "Done! Lore initialized at $LoreDir/"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $LoreDir/identity.md to describe your project"
Write-Host "  2. Copy the adapter snippet from $LoreDir/_adapters/ into your platform config"
Write-Host "     (e.g., CLAUDE.md for Claude Code, AGENTS.md for Codex)"
Write-Host "  3. Start working - your agent will read $LoreDir/INDEX.md on each session"
