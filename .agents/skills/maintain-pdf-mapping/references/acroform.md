# AcroForm notes

The supported official template has two pages and hundreds of mostly opaque fields
such as `Text19` and `Check Box5`. The repository copy is a development/test
fixture only and is excluded from distributions. At runtime, both CLI commands
require the user's local template through `--template`.

`PdfReader.get_fields()` is useful but parent fields and individual widgets may
differ, so inspect page annotations as well.

For each `/Annots` entry, resolve `/T` directly or through `/Parent`, and record
`/FT`, `/Rect`, `/V`, `/AS`, and `/AP` `/N` keys. PDF coordinates start at the
bottom-left. Sort by descending lower Y coordinate and ascending X coordinate to
compare widgets with extracted labels from top to bottom.

Rendering uses `PdfWriter(clone_from=reader)` so the AcroForm is retained, followed
by `update_page_form_field_values(..., auto_regenerate=False)` for each page.
Verify output by reopening it and checking `get_fields()` values; also assert page
count. Visual placement still requires coordinate correlation or viewing a marked
diagnostic PDF.

Existing mappings and compatibility checks live in `ABILITY_FIELDS`,
`SKILL_FIELDS`, `BASE_FIELDS`, `EXPECTED_TEMPLATE_FIELDS`, `validate_template()`,
and `field_values()` in `src/pc_wizard/pdf.py`.
