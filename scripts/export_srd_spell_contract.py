"""Export provenance-reviewed spell table metadata for the Rust port."""

from __future__ import annotations

import json

from pc_wizard.rules import SPELL_RULES


def main() -> None:
    values = {
        name: {
            "casting_time": rule.table_casting_time,
            "range": rule.range,
            "concentration": rule.concentration,
            "ritual": rule.ritual,
            "required_material": rule.required_material,
            "notes": rule.table_notes,
        }
        for name, rule in sorted(SPELL_RULES.items())
    }
    print(json.dumps(values, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
