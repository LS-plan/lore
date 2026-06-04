"""Lore Experience Engine — scoring, retrieval, dedup, TTL, mutation.

Ant colony inspired: pheromone = base_impact * decay^days * log2(uses+1).
Mutation (epsilon-greedy): small probability to recall cold/archived experiences.
"""

import json
import math
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from lore_framework.treap import TreapNode, insert as treap_insert, collect_top_k

IMPACT_WEIGHTS = {"critical": 10.0, "high": 7.0, "medium": 4.0, "low": 1.0}
DECAY_RATE = 0.02
EPSILON = 0.05
L1_THRESHOLD = 5.0
L2_THRESHOLD = 1.0
STALE_DAYS = 90
ARCHIVE_DAYS = 180
STATE_FILE = ".state.json"


# ---------------------------------------------------------------------------
# Frontmatter parser (minimal YAML-like)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> Dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    result: Dict = {}
    current_key: Optional[str] = None
    current_list: Optional[list] = None

    for line in text[3:end].splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- ") and current_list is not None:
            current_list.append(s[2:].strip().strip("\"'"))
            continue
        if ":" in s:
            key, _, val = s.partition(":")
            key, val = key.strip(), val.strip()
            current_key = key
            if not val:
                current_list = []
                result[key] = current_list
            elif val.startswith("[") and val.endswith("]"):
                result[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                current_list = None
            elif val.lower() in ("true", "false"):
                result[key] = val.lower() == "true"
                current_list = None
            else:
                result[key] = val.strip("\"'")
                current_list = None
    return result


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def load_state(lore_path: Path) -> Dict:
    p = lore_path / STATE_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"enabled": True, "experiences": {}}


def save_state(lore_path: Path, state: Dict) -> None:
    (lore_path / STATE_FILE).write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def is_enabled(lore_path: Path) -> bool:
    return not (lore_path / ".disabled").exists()


# ---------------------------------------------------------------------------
# Experience loading
# ---------------------------------------------------------------------------

def load_experiences(lore_path: Path) -> List[Dict]:
    exp_dir = lore_path / "experiences"
    if not exp_dir.exists():
        return []
    exps = []
    for f in sorted(exp_dir.glob("*.md")):
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm.get("id"):
            fm["id"] = f.stem
        fm["_file"] = str(f)
        exps.append(fm)
    return exps


# ---------------------------------------------------------------------------
# Scoring (ant colony pheromone)
# ---------------------------------------------------------------------------

def compute_score(exp: Dict, state: Dict, today: datetime) -> float:
    base = IMPACT_WEIGHTS.get(exp.get("impact", "medium"), 4.0)

    es = state.get("experiences", {}).get(exp["id"], {})
    use_count = es.get("use_count", 0)
    last_str = es.get("last_used") or exp.get("verified", "")

    days = 30
    if last_str:
        try:
            days = max((today - datetime.strptime(last_str, "%Y-%m-%d")).days, 0)
        except ValueError:
            pass

    decay = (1 - DECAY_RATE) ** days
    freq = math.log2(use_count + 1) + 1
    return base * decay * freq


def layer_of(score: float) -> str:
    if score > L1_THRESHOLD:
        return "L1"
    if score > L2_THRESHOLD:
        return "L2"
    return "L3"


# ---------------------------------------------------------------------------
# Keyword relevance (Jaccard on word tokens)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set:
    return set(re.findall(r"[\w一-鿿]+", text.lower()))


def keyword_relevance(task: str, exp: Dict) -> float:
    tw = _tokenize(task)
    if not tw:
        return 0.0

    triggers = exp.get("triggers", [])
    if isinstance(triggers, str):
        triggers = [triggers]
    scope = exp.get("scope", [])
    if isinstance(scope, str):
        scope = [scope]

    ew = _tokenize(" ".join(triggers + scope))
    if not ew:
        return 0.0

    inter = tw & ew
    union = tw | ew
    return len(inter) / len(union) if union else 0.0


# ---------------------------------------------------------------------------
# Suggest (hybrid retrieval + mutation)
# ---------------------------------------------------------------------------

def suggest(
    lore_path: Path,
    task: str,
    count: int = 5,
    alpha: float = 0.6,
) -> List[Dict]:
    state = load_state(lore_path)
    all_exps = load_experiences(lore_path)
    if not all_exps:
        return []

    today = datetime.now()

    active_exps = [e for e in all_exps if e.get("status", "active") != "archived"]
    archived_exps = [e for e in all_exps if e.get("status") == "archived"]

    root: Optional[TreapNode] = None
    score_map: Dict[str, float] = {}

    for exp in active_exps:
        s = compute_score(exp, state, today)
        score_map[exp["id"]] = s
        root = treap_insert(root, s, exp["id"])

    exp_by_id = {e["id"]: e for e in all_exps}
    max_score = max(score_map.values()) if score_map else 1.0

    candidates = []
    for eid, exp in ((e["id"], e) for e in active_exps):
        rel = keyword_relevance(task, exp)
        ts = score_map.get(eid, 0.0)
        ns = ts / max_score if max_score > 0 else 0.0
        final = alpha * rel + (1 - alpha) * ns

        candidates.append({
            "id": eid,
            "treap_score": round(ts, 3),
            "relevance": round(rel, 3),
            "final_score": round(final, 3),
            "layer": layer_of(ts),
            "triggers": exp.get("triggers", []),
            "impact": exp.get("impact", "medium"),
            "status": exp.get("status", "active"),
        })

    candidates.sort(key=lambda c: c["final_score"], reverse=True)
    result = candidates[: max(count - 1, 1)]

    # Mutation: epsilon chance to recall a cold or archived experience
    if random.random() < EPSILON:
        cold = [c for c in candidates if c["layer"] == "L3" and c not in result]
        for ae in archived_exps:
            cold.append({
                "id": ae["id"],
                "treap_score": 0.0,
                "relevance": keyword_relevance(task, ae),
                "final_score": 0.0,
                "layer": "L3",
                "triggers": ae.get("triggers", []),
                "impact": ae.get("impact", "medium"),
                "status": "archived",
            })
        if cold:
            m = random.choice(cold)
            m["mutation"] = True
            result.append(m)

    return result[:count]


# ---------------------------------------------------------------------------
# Record usage (called after agent loads an experience)
# ---------------------------------------------------------------------------

def record_usage(lore_path: Path, exp_id: str) -> None:
    state = load_state(lore_path)
    exps = state.setdefault("experiences", {})
    entry = exps.setdefault(exp_id, {"use_count": 0})
    entry["use_count"] = entry.get("use_count", 0) + 1
    entry["last_used"] = datetime.now().strftime("%Y-%m-%d")
    save_state(lore_path, state)


# ---------------------------------------------------------------------------
# Dedup check
# ---------------------------------------------------------------------------

def check_dedup(
    lore_path: Path, new_triggers: List[str], threshold: float = 0.7
) -> List[Dict]:
    exps = load_experiences(lore_path)
    new_words = set()
    for t in new_triggers:
        new_words.update(_tokenize(t))
    if not new_words:
        return []

    similar = []
    for exp in exps:
        triggers = exp.get("triggers", [])
        if isinstance(triggers, str):
            triggers = [triggers]
        ew = set()
        for t in triggers:
            ew.update(_tokenize(t))
        if not ew:
            continue
        jaccard = len(new_words & ew) / len(new_words | ew)
        if jaccard >= threshold:
            similar.append({"id": exp["id"], "similarity": round(jaccard, 3), "triggers": triggers})
    return similar


# ---------------------------------------------------------------------------
# TTL management
# ---------------------------------------------------------------------------

def update_ttl(lore_path: Path, dry_run: bool = False) -> Dict:
    state = load_state(lore_path)
    exps = load_experiences(lore_path)
    today = datetime.now()
    summary: Dict[str, list] = {"stale": [], "archived": [], "exempt": []}

    for exp in exps:
        eid = exp["id"]
        status = exp.get("status", "active")
        impact = exp.get("impact", "medium")

        if impact == "critical":
            if status in ("stale", "archived"):
                summary["exempt"].append(eid)
            continue

        es = state.get("experiences", {}).get(eid, {})
        last_str = es.get("last_used") or exp.get("verified", "")
        if not last_str:
            continue

        try:
            last = datetime.strptime(last_str, "%Y-%m-%d")
        except ValueError:
            continue

        days = (today - last).days

        if days >= ARCHIVE_DAYS and status != "archived":
            summary["archived"].append(eid)
            if not dry_run:
                _set_status(exp, "archived")
        elif days >= STALE_DAYS and status == "active":
            summary["stale"].append(eid)
            if not dry_run:
                _set_status(exp, "stale")

    return summary


def _set_status(exp: Dict, new_status: str) -> None:
    fp = Path(exp["_file"])
    if not fp.exists():
        return
    text = fp.read_text(encoding="utf-8")
    old = exp.get("status", "active")
    updated = text.replace(f"status: {old}", f"status: {new_status}", 1)
    if updated != text:
        fp.write_text(updated, encoding="utf-8")
