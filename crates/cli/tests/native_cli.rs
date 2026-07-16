use std::{
    fs,
    io::Write as _,
    path::PathBuf,
    process::{Command, Stdio},
};

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
fn validates_and_shows_the_shared_character() {
    let fixture = repository_root().join("contracts/fixtures/complete-rogue-v1.json");
    for (command, expected) in [("validate", "is valid"), ("show", "HP 9 · AC 14")] {
        let output = Command::new(executable())
            .arg(command)
            .arg(&fixture)
            .output()
            .expect("run native CLI");
        assert!(output.status.success(), "{command}: {output:?}");
        assert!(
            String::from_utf8_lossy(&output.stdout).contains(expected),
            "{command}: {output:?}"
        );
    }
}

#[test]
fn completes_a_native_interactive_fighter_and_removes_the_checkpoint() {
    let directory = std::env::temp_dir().join(format!(
        "pc-wizard-native-interactive-{}",
        std::process::id()
    ));
    if directory.exists() {
        fs::remove_dir_all(&directory).expect("clear stale directory");
    }
    fs::create_dir_all(&directory).expect("temporary directory");
    let json = directory.join("character.json");
    let pdf = directory.join("character.pdf");
    let draft = directory.join("draft.json");
    let mut child = Command::new(executable())
        .args(["create", "--template"])
        .arg(repository_root().join("assets/character-sheet.pdf"))
        .args(["--json"])
        .arg(&json)
        .args(["--output"])
        .arg(&pdf)
        .args(["--draft"])
        .arg(&draft)
        .arg("--force")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("start native wizard");
    child
        .stdin
        .take()
        .expect("stdin")
        .write_all(
            b"Native Hero\n5\n2\n2\nDwarvish,Elvish\n1\n1\n1\n1\nAthletics,Perception\nLongsword,Shortbow,Dagger\n1\n1\n1\n2\n\n\n\n1\n",
        )
        .expect("script wizard choices");
    let output = child.wait_with_output().expect("finish native wizard");
    assert!(output.status.success(), "{output:?}");
    assert!(json.is_file());
    assert!(pdf.is_file());
    assert!(!draft.exists());
    let source = fs::read_to_string(&json).expect("canonical JSON");
    assert!(source.contains("\"name\": \"Native Hero\""));
    assert!(source.contains("\"dexterity\": 16"));
    fs::remove_dir_all(directory).expect("remove temporary directory");
}

#[test]
fn end_of_input_reports_cancellation_without_writing_outputs() {
    let root = repository_root();
    let directory =
        std::env::temp_dir().join(format!("pc-wizard-native-cancel-{}", std::process::id()));
    if directory.exists() {
        fs::remove_dir_all(&directory).expect("clear stale directory");
    }
    fs::create_dir_all(&directory).expect("temporary directory");
    let json = directory.join("character.json");
    let pdf = directory.join("character.pdf");
    let output = Command::new(executable())
        .args(["create", "--template"])
        .arg(root.join("assets/character-sheet.pdf"))
        .args(["--json"])
        .arg(&json)
        .args(["--output"])
        .arg(&pdf)
        .args(["--draft"])
        .arg(directory.join("draft.json"))
        .arg("--force")
        .stdin(Stdio::null())
        .output()
        .expect("run cancelled wizard");
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("input cancelled"));
    assert!(!json.exists());
    assert!(!pdf.exists());
    fs::remove_dir_all(directory).expect("remove temporary directory");
}
