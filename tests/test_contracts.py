import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from pc_wizard.models import Character
from pc_wizard.pdf import field_values
from pc_wizard.wizard import CharacterDraft

CONTRACTS = Path(__file__).parents[1] / "contracts" / "fixtures"


def load_contract(name: str) -> dict[str, Any]:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def fingerprint(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_complete_character_and_derived_value_goldens() -> None:
    source = load_contract("complete-rogue-v1.json")
    expected = load_contract("derived-rogue-v1.json")
    character = Character.model_validate(source)

    assert character.name == "Binary Smoke Test"
    expected_fingerprint = expected.pop("golden_sha256")
    derived = character.derived_values.model_dump(mode="json")
    assert all(derived[field] == value for field, value in expected.items())
    assert fingerprint(derived) == expected_fingerprint


def test_incomplete_draft_golden_loads() -> None:
    source = load_contract("draft-origin-v1.json")
    assert CharacterDraft.model_validate(source).model_dump(mode="json") == source


def test_unknown_fields_remain_a_structured_validation_error() -> None:
    source = load_contract("invalid-unknown-field-v1.json")

    with pytest.raises(ValidationError) as raised:
        Character.model_validate(source)

    errors = raised.value.errors(include_url=False)
    assert any(
        error["loc"] == ("migration_probe",) and error["type"] == "extra_forbidden"
        for error in errors
    )


def test_pdf_projection_golden() -> None:
    source = load_contract("complete-rogue-v1.json")
    expected = load_contract("pdf-rogue-v1.json")
    values = field_values(Character.model_validate(source))

    assert len(values) == expected["field_count"]
    assert fingerprint(values) == expected["projection_sha256"]
    assert all(values[field] == value for field, value in expected["required_values"].items())


def test_rendered_page_golden_describes_a_visible_region_contract() -> None:
    expected = load_contract("rendered-page-v1.json")
    rogue = expected["scenarios"]["complete-rogue-v1"]

    assert rogue["page"] == 0
    assert rogue["minimum_changed_pixels"] > 0
    assert all(len(region) == 4 for region in rogue["regions"])
