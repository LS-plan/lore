"""FHQ-Treap (Split-Merge Treap) for experience scoring and retrieval.

A balanced BST ordered by score (key) with random priorities (heap property).
All operations are O(log n) expected time via split/merge — no rotations needed.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class TreapNode:
    score: float
    exp_id: str
    priority: int = field(default_factory=lambda: random.randint(0, (1 << 31) - 1))
    size: int = 1
    left: Optional["TreapNode"] = None
    right: Optional["TreapNode"] = None


def _size(node: Optional[TreapNode]) -> int:
    return node.size if node else 0


def _push_up(node: TreapNode) -> None:
    node.size = 1 + _size(node.left) + _size(node.right)


def split(
    root: Optional[TreapNode], key: float
) -> Tuple[Optional[TreapNode], Optional[TreapNode]]:
    """Split into (score <= key, score > key)."""
    if root is None:
        return None, None
    if root.score <= key:
        root.right, right = split(root.right, key)
        _push_up(root)
        return root, right
    else:
        left, root.left = split(root.left, key)
        _push_up(root)
        return left, root


def merge(
    left: Optional[TreapNode], right: Optional[TreapNode]
) -> Optional[TreapNode]:
    """Merge two treaps. All keys in left must be <= all keys in right."""
    if left is None:
        return right
    if right is None:
        return left
    if left.priority > right.priority:
        left.right = merge(left.right, right)
        _push_up(left)
        return left
    else:
        right.left = merge(left, right.left)
        _push_up(right)
        return right


def insert(root: Optional[TreapNode], score: float, exp_id: str) -> TreapNode:
    node = TreapNode(score=score, exp_id=exp_id)
    left, right = split(root, score)
    return merge(merge(left, node), right)


def collect_top_k(root: Optional[TreapNode], k: int) -> List[Tuple[str, float]]:
    """Top-k nodes by score (highest first). Returns [(exp_id, score), ...]."""
    result: List[Tuple[str, float]] = []
    _desc(root, result, k)
    return result


def collect_all(root: Optional[TreapNode]) -> List[Tuple[str, float]]:
    """All nodes in descending score order."""
    result: List[Tuple[str, float]] = []
    _desc_all(root, result)
    return result


def _desc(node: Optional[TreapNode], out: list, k: int) -> None:
    if node is None or len(out) >= k:
        return
    _desc(node.right, out, k)
    if len(out) < k:
        out.append((node.exp_id, node.score))
    _desc(node.left, out, k)


def _desc_all(node: Optional[TreapNode], out: list) -> None:
    if node is None:
        return
    _desc_all(node.right, out)
    out.append((node.exp_id, node.score))
    _desc_all(node.left, out)
