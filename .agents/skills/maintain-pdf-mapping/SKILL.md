---
name: maintain-pdf-mapping
description: Inspect, diagnose, test, or update pc-wizard's pypdf AcroForm rendering and opaque character-sheet.pdf field mappings. Use for missing, misplaced, malformed, or new PDF values, checkbox states, appearance streams, and changes to src/pc_wizard/pdf.py; do not use for game-rule changes with no PDF impact.
---

# Maintain PDF mapping

Map fields from evidence: form metadata, annotation rectangles, visible labels,
and write/read-back tests. The template's names are opaque and must not be guessed.

## Workflow

1. Read `references/acroform.md` before changing mappings.
2. Inspect the repository's development-only `character-sheet.pdf` fixture, or the
   explicit user-supplied template under diagnosis, with `pypdf`. Capture field
   name, type, page, rectangle, parent field, current value, and checkbox
   appearance states.
3. Correlate annotation coordinates with extracted page labels. If ambiguity
   remains, create a temporary diagnostic PDF with unmistakable marker values and
   inspect it; never commit diagnostic output.
4. Update `field_values()` for text projections. Keep calculations on `Character`.
5. Handle buttons with their actual on-state name rather than assuming `/Yes`.
6. Keep `EXPECTED_TEMPLATE_FIELDS` and `validate_template()` aligned with any new
   mapped fields.
7. Render a sample through an explicit template path, reopen it with `PdfReader`,
   and assert stored values. Preserve both pages and the AcroForm.
8. Add or update `tests/test_pdf.py`, then invoke `$verify-pc-wizard`.

## Safety

- Never overwrite `character-sheet.pdf`.
- Never copy the official template into package assets or release artifacts.
- Do not flatten the form unless explicitly requested.
- Do not infer semantic meaning from numeric field names alone.
- Keep mapping constants centralized in `pdf.py`.
