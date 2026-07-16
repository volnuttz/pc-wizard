# Compatibility contracts

These fixtures and the executable test runner are the migration boundary. They
must run unchanged against the Python reference and the Rust executable. The
JSON document is the canonical character record; rendered PDFs are views of it.

Run the reference suite from the repository root:

```console
uv run python scripts/contract_test.py --executable .venv/bin/pc-wizard
```

On Windows, pass `.venv\\Scripts\\pc-wizard.exe`. The future Rust binary uses
the same invocation. `--template` must always name a separately supplied copy of
the supported official template; the checked-in file is a development fixture.

`cli-v1.md` defines the stable externally visible behavior. Its scenario IDs are
used in benchmark output and must not be renamed without a compatibility-version
bump.

`character-json-v1.md` defines the current character schema. The `fixtures/`
directory contains complete, draft, invalid-input, derived-value, PDF-projection,
and rendered-page golden cases. Projection fingerprints cover every supported PDF
field, including intentionally blank ones; the named required values make the
opaque field contract reviewable.
