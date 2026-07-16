use std::{path::PathBuf, process::Command};

fn repository_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .expect("repository root")
}

fn executable() -> &'static str {
    env!("CARGO_BIN_EXE_pc-wizard")
}

#[test]
fn validates_and_shows_the_smoke_character() {
    let fixture = repository_root().join("fixtures/complete-character.json");
    for (command, expected) in [("validate", "is valid"), ("show", "HP 9 · AC 14")] {
        let output = Command::new(executable())
            .arg(command)
            .arg(&fixture)
            .output()
            .expect("run CLI");
        assert!(output.status.success(), "{command}: {output:?}");
        assert!(
            String::from_utf8_lossy(&output.stdout).contains(expected),
            "{command}: {output:?}"
        );
    }
}
