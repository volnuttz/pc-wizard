use std::{collections::BTreeMap, fs, path::PathBuf};

use lopdf::{Document, Object};
use pc_wizard_domain::Character;
use pc_wizard_pdf_renderer::{
    acroform_inventory, read_field_values, render_character, render_fields, template_inventory,
};
use serde::Deserialize;

fn repository_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .expect("root")
}

#[derive(Deserialize)]
struct TemplateContract {
    page_count: usize,
    field_count: usize,
    field_type_counts: FieldTypeCounts,
    inventory_sha256: String,
}

#[derive(Deserialize)]
struct FieldTypeCounts {
    #[serde(rename = "/Btn")]
    button: usize,
    #[serde(rename = "/Tx")]
    text: usize,
    #[serde(rename = "None")]
    untyped: usize,
}

#[derive(Deserialize)]
struct FullProjectionContract {
    values: BTreeMap<String, String>,
}

#[derive(Deserialize)]
struct MatrixRecord {
    character: serde_json::Value,
    derived: MatrixDerived,
}

#[derive(Deserialize)]
struct MatrixDerived {
    armor_class: i16,
}

#[derive(Deserialize)]
struct OriginMatrix {
    backgrounds: Vec<MatrixRecord>,
    species: Vec<MatrixRecord>,
}

fn full_projection_contract(root: &std::path::Path) -> FullProjectionContract {
    serde_json::from_str(
        &fs::read_to_string(root.join("contracts/fixtures/pdf-projection-full-v1.json"))
            .expect("projection contract"),
    )
    .expect("valid projection contract")
}

fn appearance_content(path: &std::path::Path, field_name: &str) -> String {
    let document = Document::load(path).expect("rendered PDF");
    for page_id in document.get_pages().into_values() {
        let page = document
            .get_object(page_id)
            .and_then(Object::as_dict)
            .expect("page");
        let (_, annotations) = document
            .dereference(page.get(b"Annots").expect("annotations"))
            .expect("annotation array");
        for annotation in annotations.as_array().expect("annotation array") {
            let widget_id = annotation.as_reference().expect("widget reference");
            let widget = document
                .get_object(widget_id)
                .and_then(Object::as_dict)
                .expect("widget");
            let name = widget
                .get(b"T")
                .ok()
                .and_then(|value| value.as_str().ok())
                .map(|value| String::from_utf8_lossy(value).into_owned());
            if name.as_deref() != Some(field_name) {
                continue;
            }
            let (_, appearance) = document
                .dereference(
                    widget
                        .get(b"AP")
                        .and_then(Object::as_dict)
                        .and_then(|value| value.get(b"N"))
                        .expect("normal appearance"),
                )
                .expect("appearance stream");
            return String::from_utf8_lossy(
                &appearance.as_stream().expect("appearance stream").content,
            )
            .into_owned();
        }
    }
    panic!("field appearance not found: {field_name}");
}

#[test]
fn renderer_enumerates_the_supported_template_before_writing() {
    let root = repository_root();
    let expected: TemplateContract = serde_json::from_str(
        &fs::read_to_string(root.join("contracts/fixtures/template-fields-v1.json"))
            .expect("template contract"),
    )
    .expect("valid template contract");
    let actual = template_inventory(root.join("assets/character-sheet.pdf")).expect("inventory");

    assert_eq!(actual.page_count, expected.page_count);
    assert_eq!(actual.field_count, expected.field_count);
    assert_eq!(actual.text_field_count, expected.field_type_counts.text);
    assert_eq!(actual.button_field_count, expected.field_type_counts.button);
    assert_eq!(
        actual.untyped_field_count,
        expected.field_type_counts.untyped
    );
    assert_eq!(actual.sha256, expected.inventory_sha256);
}

#[test]
fn renderer_enumerates_the_complete_acroform_catalog() {
    let root = repository_root();
    let expected: TemplateContract = serde_json::from_str(
        &fs::read_to_string(root.join("contracts/fixtures/template-catalog-v1.json"))
            .expect("catalog contract"),
    )
    .expect("valid catalog contract");
    let actual = acroform_inventory(root.join("assets/character-sheet.pdf")).expect("catalog");
    assert_eq!(actual.page_count, expected.page_count);
    assert_eq!(actual.field_count, expected.field_count);
    assert_eq!(actual.text_field_count, expected.field_type_counts.text);
    assert_eq!(actual.button_field_count, expected.field_type_counts.button);
    assert_eq!(
        actual.untyped_field_count,
        expected.field_type_counts.untyped
    );
    assert_eq!(actual.sha256, expected.inventory_sha256);
}

#[test]
fn generic_renderer_reads_back_every_frozen_projected_field() {
    let root = repository_root();
    let directory =
        std::env::temp_dir().join(format!("pc-wizard-full-proof-{}", std::process::id()));
    fs::create_dir_all(&directory).expect("temporary directory");
    let contract = full_projection_contract(&root);
    let output = directory.join("sheet.pdf");
    render_fields(
        root.join("assets/character-sheet.pdf"),
        &output,
        &contract.values,
    )
    .expect("render full projection");

    let actual_values =
        read_field_values(&output, contract.values.keys().cloned()).expect("read projected fields");
    for (field, expected) in &contract.values {
        let actual = actual_values.get(field).expect("read projected field");
        if let Some(name) = expected.strip_prefix('/') {
            assert_eq!(*actual, Object::Name(name.as_bytes().to_vec()), "{field}");
        } else {
            assert_eq!(
                actual.as_str().expect("text value"),
                expected.as_bytes(),
                "{field}"
            );
        }
    }
    fs::remove_dir_all(directory).expect("remove temporary proof directory");
}

#[test]
fn production_projection_matches_the_python_oracle() {
    let root = repository_root();
    let directory =
        std::env::temp_dir().join(format!("pc-wizard-production-proof-{}", std::process::id()));
    fs::create_dir_all(&directory).expect("temporary directory");
    let contract = full_projection_contract(&root);
    let source = fs::read_to_string(root.join("contracts/fixtures/complete-rogue-v1.json"))
        .expect("character fixture");
    let character = Character::from_json(&source).expect("valid character");
    let output = directory.join("sheet.pdf");
    render_character(&character, root.join("assets/character-sheet.pdf"), &output)
        .expect("production render");
    let actual_values = read_field_values(&output, contract.values.keys().cloned())
        .expect("read production fields");
    let mut differences = Vec::new();
    for (field, expected) in &contract.values {
        let actual = actual_values.get(field).expect("read projected field");
        let matches = if let Some(name) = expected.strip_prefix('/') {
            *actual == Object::Name(name.as_bytes().to_vec())
        } else {
            actual
                .as_str()
                .is_ok_and(|value| value == expected.as_bytes())
        };
        if !matches {
            differences.push(format!("{field}: expected {expected:?}, got {actual:?}"));
        }
    }
    assert!(
        differences.is_empty(),
        "production projection differences:\n{}",
        differences.join("\n")
    );
    let attack_appearance = appearance_content(&output, "Text33");
    let font_size: f32 = attack_appearance
        .split("/Helv ")
        .nth(1)
        .and_then(|value| value.split(" Tf").next())
        .expect("font size")
        .parse()
        .expect("numeric font size");
    assert!((0.0..12.0).contains(&font_size));
    assert!(attack_appearance.contains(" Tj"));
    assert!(appearance_content(&output, "Text54").matches(" Td").count() > 2);
    fs::remove_dir_all(directory).expect("remove temporary proof directory");
}

#[test]
fn production_renderer_covers_every_class_background_and_species_fixture() {
    let root = repository_root();
    let mut records: Vec<MatrixRecord> = serde_json::from_str(
        &fs::read_to_string(root.join("contracts/fixtures/class-parity-v1.json"))
            .expect("class matrix"),
    )
    .expect("valid class matrix");
    let origins: OriginMatrix = serde_json::from_str(
        &fs::read_to_string(root.join("contracts/fixtures/origin-parity-v1.json"))
            .expect("origin matrix"),
    )
    .expect("valid origin matrix");
    records.extend(origins.backgrounds);
    records.extend(origins.species);
    let directory = std::env::temp_dir().join(format!(
        "pc-wizard-production-matrix-{}",
        std::process::id()
    ));
    fs::create_dir_all(&directory).expect("temporary directory");
    for (index, record) in records.into_iter().enumerate() {
        let character = Character::from_json(&record.character.to_string()).expect("character");
        let output = directory.join(format!("{index}.pdf"));
        render_character(&character, root.join("assets/character-sheet.pdf"), &output)
            .expect("production render");
        let values = read_field_values(
            &output,
            ["Text7", "Text8", "Text13"].into_iter().map(str::to_owned),
        )
        .expect("read production identity");
        for (field, expected) in [
            ("Text7", character.character_class.as_str()),
            ("Text8", character.species.as_str()),
        ] {
            assert_eq!(
                values[field].as_str().expect("text"),
                expected.as_bytes(),
                "{} / {} / {field}",
                character.character_class,
                character.species
            );
        }
        assert_eq!(
            values["Text13"].as_str().expect("armor class"),
            record.derived.armor_class.to_string().as_bytes(),
            "{} / {} armor class",
            character.character_class,
            character.species
        );
    }
    fs::remove_dir_all(directory).expect("remove temporary directory");
}
