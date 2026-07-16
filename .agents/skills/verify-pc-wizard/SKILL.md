---
name: verify-pc-wizard
description: Validate pc-wizard changes and diagnose failures using the pinned Rust workspace quality gate. Use before handoff, after implementation, when CI or local lint/test/audit checks fail, or when CLI and PDF behavior needs targeted verification.
---

# Verify pc-wizard

Run checks from the repository root with Cargo. Fix failures caused by the current
change without rewriting unrelated user work.

## Workflow

1. Inspect the diff and choose targeted checks while iterating:
   - Models or rules: `cargo +1.88.0 test -p pc-wizard-domain`
   - Wizard prompts: `cargo +1.88.0 test -p pc-wizard-creation -p pc-wizard-cli`
   - PDF mapping: `cargo +1.88.0 test -p pc-wizard-integration-tests --test pdf_proof`
   - CLI surface: build `pc-wizard-cli`, then run command-specific help
   - Release packaging: build `pc-wizard-cli --release --locked`, exercise the
     complete JSON/PDF smoke path, and inspect the archive contents
   - Actions changes: parse every edited workflow as YAML before relying on CI
2. Run the complete gate before handoff:

   ```console
   cargo +1.88.0 fmt --check
   cargo +1.88.0 clippy --workspace --all-targets -- -D warnings
   cargo +1.88.0 test --workspace --locked
   cargo +1.88.0 audit
   cargo +1.88.0 deny check
   ```

3. If a check fails, report the exact failure, identify whether it is related to
   the current work, make the narrowest appropriate fix, and rerun the failed
   check plus the full gate.
4. For PDF changes, require a real render/read-back test. For CLI changes, require
   help output. For native-binary changes, build and smoke-test the release binary:

   ```console
   cargo +1.88.0 build --release --locked -p pc-wizard-cli
   target/release/pc-wizard create --template assets/character-sheet.pdf \
     --from-json contracts/fixtures/complete-rogue-v1.json \
     --json /tmp/character.json --output /tmp/character.pdf --force
   ```

   Do not claim interactive behavior was verified when only unit tests ran. Do not
   claim a platform build or GitHub Release passed until its Actions run or release
   assets were inspected.

## Handoff

State the commands run and concise results. Mention checks that could not run and
why. Never describe a partial gate as fully passing.
