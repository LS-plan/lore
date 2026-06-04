"""Global Lore registry at ~/.lore/ — tracks all projects using Lore."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

GLOBAL_DIR = Path.home() / ".lore"
REGISTRY_FILE = GLOBAL_DIR / "registry.json"


def _ensure_global_dir() -> None:
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)


def _load_registry() -> List[Dict]:
    if not REGISTRY_FILE.exists():
        return []
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_registry(entries: List[Dict]) -> None:
    _ensure_global_dir()
    REGISTRY_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def register_project(project_path: str, project_name: str, phase: str) -> None:
    entries = _load_registry()
    norm_path = str(Path(project_path).resolve())

    for entry in entries:
        if entry.get("path") == norm_path:
            entry["name"] = project_name
            entry["phase"] = phase
            entry["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_registry(entries)
            return

    entries.append({
        "path": norm_path,
        "name": project_name,
        "phase": phase,
        "registered": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    _save_registry(entries)


def touch_project(project_path: str) -> None:
    entries = _load_registry()
    norm_path = str(Path(project_path).resolve())
    for entry in entries:
        if entry.get("path") == norm_path:
            entry["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_registry(entries)
            return


def list_projects() -> List[Dict]:
    return _load_registry()


def get_global_stats() -> Dict:
    """Aggregate stats across all registered projects."""
    from lore_framework.constants import LORE_DIR
    from lore_framework.engine import load_experiences, load_state, compute_score, layer_of

    entries = _load_registry()
    stats = {
        "projects": len(entries),
        "total_experiences": 0,
        "total_patterns": 0,
        "layers": {"L1": 0, "L2": 0, "L3": 0},
        "statuses": {},
        "per_project": [],
    }

    today = datetime.now()

    for entry in entries:
        p = Path(entry["path"]) / LORE_DIR
        if not p.exists():
            stats["per_project"].append({
                "name": entry["name"], "path": entry["path"], "status": "missing",
            })
            continue

        exps = load_experiences(p)
        state = load_state(p)
        patterns_dir = p / "patterns"
        pattern_count = len([f for f in patterns_dir.glob("*.md") if f.name != "INDEX.md"]) if patterns_dir.exists() else 0

        proj_layers = {"L1": 0, "L2": 0, "L3": 0}
        for exp in exps:
            s = compute_score(exp, state, today)
            layer = layer_of(s)
            proj_layers[layer] += 1
            stats["layers"][layer] += 1
            st = exp.get("status", "active")
            stats["statuses"][st] = stats["statuses"].get(st, 0) + 1

        stats["total_experiences"] += len(exps)
        stats["total_patterns"] += pattern_count
        stats["per_project"].append({
            "name": entry["name"],
            "path": entry["path"],
            "experiences": len(exps),
            "patterns": pattern_count,
            "layers": proj_layers,
            "phase": entry.get("phase", "unknown"),
            "last_active": entry.get("last_active", "—"),
        })

    return stats
