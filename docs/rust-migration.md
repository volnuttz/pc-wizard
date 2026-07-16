# Rust migration foundation

Python 3.13 is the behavioral reference until a native implementation passes the
shared compatibility scenarios in [`../contracts`](../contracts). This migration
does not change the level-1 SRD scope, canonical JSON status, or requirement for
an externally supplied official character-sheet PDF.

## Workspace boundaries

The Cargo workspace is intentionally dependency-free while compatibility cases
are frozen:

| Crate | Responsibility |
| --- | --- |
| `pc-wizard-srd-data` | SRD-derived tables and stable identifiers, with source provenance |
| `pc-wizard-domain` | canonical models, validation, and derived values |
| `pc-wizard-creation` | wizard state machine, drafts, review, and cancellation |
| `pc-wizard-pdf-renderer` | template validation, AcroForm writing, read-back, visual parity |
| `pc-wizard-cli` | arguments, exit codes, terminal presentation, and file coordination |
| `pc-wizard-integration-tests` | Rust tests that consume shared contract fixtures |

Dependencies point inward only: CLI depends on creation/domain/PDF; creation and
PDF depend on domain; domain depends on SRD data. This prevents terminal or PDF
types from entering rule and validation code.

## Library evaluation and decision gates

Candidates to evaluate in the proof of concept are `clap` (arguments),
`dialoguer` plus `console` (prompts and terminal output), `serde` plus
`serde_json` (canonical JSON), `miette` (diagnostic errors), and `lopdf` (PDF).
These are candidates, not approved dependencies. The standard library cannot
provide robust JSON serialization, interactive terminal controls, or AcroForm
editing; each selected dependency will be pinned in `Cargo.lock` and justified in
its implementation change.

PDF output is the highest-risk decision. Before selecting a PDF crate, a spike
must use `assets/character-sheet.pdf` to prove all of the following:

1. enumerate and validate the two-page field set;
2. write a text field and an on/off checkbox with correct appearance streams;
3. preserve the filled values in a PDF read-back; and
4. produce a visually readable rendered page, including long-text sizing.

Failure on any item means evaluate another library or retain a narrowly scoped
compatibility bridge; it is not acceptable to declare a library selected from API
documentation alone.

## Quality and release policy

- Minimum supported Rust is 1.85.0 (edition 2024); `rust-toolchain.toml` pins it.
- Before Rust code lands: `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace`.
- Before publishing: add `cargo audit`, a license review (`cargo deny` or an
  equivalent locked policy), locked cross-platform builds, and the shared
  executable contract suite to CI.
- A Python and Rust artifact run side-by-side until the Rust artifact meets the
  accepted performance and PDF-parity targets on Linux x86-64, Windows x86-64,
  macOS ARM64, and macOS x86-64.

## Staged cutover and rollback

Port and prove `show`, non-interactive `create`, and template/PDF rendering
before the interactive wizard. Each slice must pass its shared scenarios against
both executables. Publish a prerelease native binary only after PDF parity; keep
the Python artifact available throughout the prerelease and one stable release
after cutover. Roll back the default download if a current-schema JSON fixture,
PDF field/read-back/visual fixture, or supported platform fails parity.

## Benchmark protocol

`scripts/benchmark_cli.py` records reproducible scenario timings for either
executable. It makes no performance claim by itself: run it on each supported OS,
first with the Python `uv run pc-wizard` command and then with one-file and
one-directory release artifacts. Preserve emitted JSON under an approved
benchmark-results location when CI storage is selected.

Required metrics are cold and warm latency, scenario wall time, peak memory,
artifact/download size, and one-file extraction overhead. Cold runs must clear
the one-file extraction cache according to the release packager's documented
platform behavior; warm runs must use the same executable after that first run.
Profile separately: Python imports, validation/derivation, prompt rendering, PDF
parsing, AcroForm updates, and file I/O. Acceptance targets will be set only after
representative baselines exist on all four platforms.

