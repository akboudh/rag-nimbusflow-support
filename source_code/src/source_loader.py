from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(root: Path) -> list[dict[str, Any]]:
    manifest_path = root / "data" / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load_source_content(root: Path, entry: dict[str, Any]) -> Any:
    path = root / entry["path"]
    if path.suffix == ".json":
      return json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8")
