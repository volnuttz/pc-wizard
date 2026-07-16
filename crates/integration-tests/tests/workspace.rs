#[test]
fn shared_contract_directory_is_present() {
    assert!(std::path::Path::new("../../contracts").is_dir());
}
