# Compatibility contracts

These fixtures are the frozen migration boundary. They were generated from the
Python 0.2.1 oracle and now run directly in the Rust domain, CLI, and PDF tests.
The JSON document is canonical; rendered PDFs are views of it.

Run the native contract suite from the repository root:

```console
cargo +1.88.0 test --workspace --locked
```

The release workflow repeats native binary scenarios on every supported platform.
`--template` must always name a separately supplied copy of
the supported official template; the checked-in file is a development fixture.

`cli-v1.md` defines the stable externally visible behavior. Its scenario IDs are
used in benchmark output and must not be renamed without a compatibility-version
bump.

`character-json-v1.md` defines the current character schema. The `fixtures/`
directory contains complete, draft, invalid-input, derived-value, PDF-projection,
and rendered-page golden cases. Projection fingerprints cover every supported PDF
field, including intentionally blank ones; the named required values make the
opaque field contract reviewable.

`pdf-projection-full-v1.json` is the complete 375-value oracle map used by the
production renderer test. Class and origin matrices cover all 12 classes, all 4
backgrounds, and all 9 species. Regenerate these fixtures only during an explicit
compatibility-contract revision, never as part of ordinary test execution.
