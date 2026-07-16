"""Export a complete, canonical PDF field-value contract from a character JSON file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pc_wizard.models import Character
from pc_wizard.pdf import field_values


def projection_contract(character_path: Path) -> dict[str, object]:
    """Build a stable full field map suitable for cross-implementation comparison."""
    character = Character.load_json(character_path)
    values = field_values(character)
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "character": character_path.name,
        "field_count": len(values),
        "projection_sha256": hashlib.sha256(canonical).hexdigest(),
        "values": dict(sorted(values.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("character", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    output = json.dumps(projection_contract(arguments.character), indent=2, sort_keys=True) + "\n"
    arguments.output.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
