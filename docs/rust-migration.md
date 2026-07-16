# Rust migration

The production application is a Rust 1.88.0 workspace. Python 0.2.1 served as the
behavioral oracle; its final outputs are frozen under `contracts/fixtures/` and no
Python process is required by Rust tests, builds, packages, or releases.

## Architecture

| Crate | Responsibility |
| --- | --- |
| `pc-wizard-srd-data` | SRD-derived tables and stable identifiers |
| `pc-wizard-domain` | canonical Serde models, validation, and derived values |
| `pc-wizard-creation` | native wizard stages, drafts, review, and resume |
| `pc-wizard-pdf-renderer` | template validation, projection, AcroForm writing, and read-back |
| `pc-wizard-cli` | arguments, exit codes, terminal presentation, and file coordination |
| `pc-wizard-integration-tests` | frozen contracts and production PDF tests |

Dependencies point inward: CLI depends on creation/domain/PDF; creation and PDF
depend on domain; domain depends on SRD data. JSON remains the canonical record.

## Compatibility evidence

- The complete current-schema Rogue fixture round-trips through Serde, while
  unknown fields and invalid closed/cross-field choices are rejected.
- Class parity covers all 12 SRD level-1 classes, including derived inventory,
  attacks, defenses, skills, spells, profiles, slots, and class resources.
- Origin parity covers all 4 backgrounds and 9 species. A checked spell contract
  preserves the metadata for every spell exposed during level-1 creation.
- Native CLI tests cover help/version, validate, show, non-interactive creation,
  template failures, complete interactive creation, checkpoint removal, and
  cancellation without partial final outputs.
- The supported PDF contract verifies two pages, 244 named widgets, the complete
  425-entry AcroForm tree, and all 375 projected values. Production matrix renders
  cover every class, background, and species fixture.

The official template is always external and supplied through `--template`.

## Dependency decisions

- `serde` and `serde_json` provide stable canonical JSON modeling unavailable in
  the standard library.
- `lopdf` 0.43 performs direct AcroForm object updates, recursive field indexing,
  dynamic checkbox appearance-state selection, and read-back. Optional features
  are disabled because date conversion is unnecessary.
- `rand` supplies operating-system-seeded 4d6 generation; the standard library
  has no random-number generator.
- `sha2` fingerprints the supported field catalogs.
- The CLI and prompt surface intentionally use the standard library to keep the
  optimized binary and startup path small.

`lopdf` requires Rust 1.88, which therefore defines the MSRV. `cargo-deny` records
the accepted licenses and the narrow temporary allowance for the unmaintained
`ttf-parser` advisory inherited through lopdf; there is no safe compatible upgrade
at the migration baseline.

## Quality, release, and rollback

The local gate is formatting, Clippy with warnings denied, full workspace tests,
`cargo audit`, and `cargo deny`. GitHub Actions repeats quality and native release
smokes on Linux x86-64, Windows x86-64, macOS ARM64, and macOS x86-64, generates
coverage, packages archives and SHA-256 files, and records per-platform native
benchmarks. Release binaries contain neither source PDF.

The former Python implementation and its uv lock remain temporarily as a rollback
oracle through the first stable native release. Production workflows do not build,
test, audit, package, or publish it. Remove that oracle only after the documented
stable-release rollback window closes.

## Acceptance targets and baseline

Native release targets are:

- warm help/version/show median below 25 ms;
- warm JSON plus PDF creation median below 500 ms;
- peak working set below 64 MiB for representative scenarios;
- executable below 10 MiB and compressed platform archive below 6 MiB;
- zero one-file extraction overhead because releases are direct native binaries.

The checked Linux x86-64 baseline passes the latency and executable-size targets:
the 1,688,352-byte (1.61 MiB) optimized binary measured approximately 2.1–2.4 ms for warm
help/version/show and 43.7 ms for warm creation. The earlier Python artifact
measured approximately 437–608 ms and 1.34 s respectively. The Native binaries
workflow records the same protocol, cold first run, warm samples, peak working
set, artifact size, and zero extraction overhead on every release platform.
