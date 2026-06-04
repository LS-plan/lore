"""lore turnoff / lore turnon — toggle Lore processing."""

import argparse
from pathlib import Path

from lore_framework.constants import LORE_DIR


def cmd_turnoff(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR
    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    marker = lore_path / ".disabled"
    if marker.exists():
        print("Lore is already turned off.")
        return 0

    marker.touch()
    print("Lore turned off. Agents will skip .lore/ processing.")
    print("Use 'lore turnon' to re-enable.")
    return 0


def cmd_turnon(args: argparse.Namespace) -> int:
    lore_path = Path.cwd() / LORE_DIR
    if not lore_path.exists():
        print(f"Error: {LORE_DIR}/ not found. Use 'lore init' first.")
        return 1

    marker = lore_path / ".disabled"
    if not marker.exists():
        print("Lore is already turned on.")
        return 0

    marker.unlink()
    print("Lore turned on. Agents will resume .lore/ processing.")
    return 0
