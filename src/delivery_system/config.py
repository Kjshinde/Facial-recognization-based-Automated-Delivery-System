"""Shared configuration helpers for command-line tools."""

import json
from pathlib import Path
from typing import Dict, Optional


DEFAULT_DATASET_DIR = Path("data/dataset")
DEFAULT_MODEL_PATH = Path("models/trainer.yml")
DEFAULT_CONFIDENCE_THRESHOLD = 80.0
DEFAULT_RELAY_PIN = 23
DEFAULT_UNLOCK_STATE = 0
DEFAULT_LOCKED_STATE = 1


def load_names(names_file: Optional[Path]) -> Dict[str, str]:
    """Load a JSON map of face IDs to display names."""
    if names_file is None:
        return {}

    if not names_file.exists():
        raise SystemExit(f"Names file not found: {names_file}")

    with names_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise SystemExit("Names file must be a JSON object, for example: {\"1\": \"Alice\"}")

    return {str(face_id): str(name) for face_id, name in data.items()}


def display_name(names: Dict[str, str], face_id: int) -> str:
    """Return the configured display name for a face ID."""
    return names.get(str(face_id), f"ID {face_id}")
