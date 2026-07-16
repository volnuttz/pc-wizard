//! Supported-template validation and `AcroForm` rendering implementation.

use std::{collections::BTreeMap, fmt::Write as _, path::Path};

use lopdf::{
    Document, Object, ObjectId, Stream,
    content::{Content, Operation},
    dictionary,
};
use pc_wizard_domain::Character;
use sha2::{Digest, Sha256};

use crate::projection::project_spell_rows;

type Result<T> = std::result::Result<T, String>;

const SUPPORTED_CATALOG_SHA256: &str =
    "211ab47d8428008778f7688b48cb69be264810d147685040e0d774ddaaa30b49";
const TEMPLATE_PAGE_URL: &str = "https://www.dndbeyond.com/resources/1779-d-d-character-sheets";
const TEMPLATE_DOWNLOAD_URL: &str =
    "https://media.dndbeyond.com/compendium-images/free-rules/ph/character-sheet.pdf";

/// Validate the exact supported two-page official character sheet.
///
/// # Errors
///
/// Returns an error when the template is unreadable or its field catalog differs
/// from the development fixture.
pub fn validate_template(template: impl AsRef<Path>) -> Result<()> {
    let template = template.as_ref();
    let inventory = acroform_inventory(template).map_err(|error| {
        format!("Unable to read PDF template {}. Download the official sheet from {TEMPLATE_PAGE_URL}. ({error})", template.display())
    })?;
    if inventory.page_count != 2
        || inventory.field_count != 425
        || inventory.text_field_count != 260
        || inventory.button_field_count != 151
        || inventory.untyped_field_count != 14
        || inventory.sha256 != SUPPORTED_CATALOG_SHA256
    {
        return Err(format!(
            "Incompatible PDF template {}. Download the supported official sheet from {TEMPLATE_DOWNLOAD_URL} (this direct URL may change; see {TEMPLATE_PAGE_URL}).",
            template.display()
        ));
    }
    Ok(())
}

/// Render the canonical identity, ability, save, skill, and combat summary fields.
///
/// # Errors
///
/// Returns an error when the supported template cannot be read or written.
#[allow(clippy::too_many_lines)]
pub fn render_character(
    character: &Character,
    template: impl AsRef<Path>,
    output: impl AsRef<Path>,
) -> Result<()> {
    validate_template(&template)?;
    let sheet = character.sheet();
    let mut values = BTreeMap::from([
        ("Text1".to_owned(), character.name.clone()),
        ("Text6".to_owned(), character.background.to_string()),
        ("Text7".to_owned(), character.character_class.to_string()),
        ("Text8".to_owned(), character.species.to_string()),
        ("Text9".to_owned(), String::new()),
        ("Text11".to_owned(), character.level.to_string()),
        ("Text12".to_owned(), character.xp.to_string()),
        ("Text13".to_owned(), character.armor_class().to_string()),
        ("Text14".to_owned(), character.hit_points().to_string()),
        ("Text15".to_owned(), String::new()),
        ("Text16".to_owned(), character.hit_points().to_string()),
        ("Text17".to_owned(), format!("1d{}", sheet.hit_die())),
        (
            "Text19".to_owned(),
            signed(i16::from(character.proficiency_bonus())),
        ),
        ("Text18".to_owned(), String::new()),
        ("Text26".to_owned(), signed(character.initiative_modifier())),
        ("Text27".to_owned(), character.speed().to_string()),
        (
            "Text28".to_owned(),
            character.size.chars().next().unwrap_or(' ').to_string(),
        ),
        (
            "Text29".to_owned(),
            character.passive_perception().to_string(),
        ),
        ("Text54".to_owned(), character.class_traits().join("\n")),
        (
            "Text55".to_owned(),
            character
                .class_resources()
                .iter()
                .map(pc_wizard_domain::ClassResource::summary)
                .collect::<Vec<_>>()
                .join("\n"),
        ),
        ("Text57".to_owned(), character.species_traits().join("\n")),
        (
            "Text58".to_owned(),
            character.origin_feat_traits().join("\n"),
        ),
        ("Text59".to_owned(), character.weapon_proficiencies()),
        (
            "Text60".to_owned(),
            character.all_tool_proficiencies().join("\n"),
        ),
        (
            "Text96".to_owned(),
            character.appearance.clone().unwrap_or_default(),
        ),
        ("Text97".to_owned(), character_details(character)),
        ("Text93".to_owned(), String::new()),
        ("Text94".to_owned(), String::new()),
        ("Text95".to_owned(), String::new()),
        ("Text111".to_owned(), String::new()),
        (
            "Text98".to_owned(),
            character_languages(character).join("\n"),
        ),
        ("Text100".to_owned(), character.alignment.clone()),
    ]);
    for (ability, score_field, modifier_field, save_field, checkbox) in [
        ("strength", "Text64", "Text21", "Text91", "Check Box37"),
        ("dexterity", "Text66", "Text22", "Text87", "Check Box33"),
        ("constitution", "Text67", "Text24", "Text86", "Check Box32"),
        ("intelligence", "Text63", "Text20", "Text69", "Check Box4"),
        ("wisdom", "Text65", "Text23", "Text75", "Check Box21"),
        ("charisma", "Text68", "Text25", "Text81", "Check Box26"),
    ] {
        values.insert(
            score_field.to_owned(),
            character.abilities.score(ability).to_string(),
        );
        values.insert(
            modifier_field.to_owned(),
            signed(character.abilities.modifier(ability)),
        );
        let save = sheet.saving_throw(ability);
        values.insert(save_field.to_owned(), signed(save.modifier));
        values.insert(
            checkbox.to_owned(),
            if save.proficient { "/Yes" } else { "/Off" }.to_owned(),
        );
    }
    for (skill, field, checkbox) in [
        ("Animal Handling", "Text76", "Check Box22"),
        ("Insight", "Text77", "Check Box23"),
        ("Medicine", "Text78", "Check Box25"),
        ("Perception", "Text79", "Check Box31"),
        ("Survival", "Text80", "Check Box24"),
        ("Deception", "Text82", "Check Box27"),
        ("Intimidation", "Text83", "Check Box28"),
        ("Performance", "Text84", "Check Box30"),
        ("Persuasion", "Text85", "Check Box29"),
        ("Acrobatics", "Text88", "Check Box34"),
        ("Sleight of Hand", "Text89", "Check Box35"),
        ("Stealth", "Text90", "Check Box36"),
        ("Athletics", "Text92", "Check Box38"),
        ("Arcana", "Text70", "Check Box16"),
        ("History", "Text71", "Check Box17"),
        ("Investigation", "Text72", "Check Box19"),
        ("Nature", "Text73", "Check Box20"),
        ("Religion", "Text74", "Check Box18"),
    ] {
        values.insert(field.to_owned(), signed(character.skill_modifier(skill)));
        values.insert(
            checkbox.to_owned(),
            if character.skills().contains(skill) {
                "/Yes"
            } else {
                "/Off"
            }
            .to_owned(),
        );
    }
    for (training, checkbox) in [
        ("Light", "Check Box13"),
        ("Medium", "Check Box14"),
        ("Heavy", "Check Box15"),
        ("Shields", "Check Box12"),
    ] {
        values.insert(
            checkbox.to_owned(),
            if character.armor_training().contains(training) {
                "/Yes"
            } else {
                "/Off"
            }
            .to_owned(),
        );
    }
    let attacks = character.weapon_attacks();
    for (index, fields) in [
        ["Text30", "Text31", "Text32", "Text33"],
        ["Text34", "Text35", "Text36", "Text37"],
        ["Text38", "Text39", "Text40", "Text41"],
        ["Text42", "Text43", "Text44", "Text45"],
        ["Text46", "Text47", "Text48", "Text49"],
        ["Text50", "Text51", "Text52", "Text53"],
    ]
    .iter()
    .enumerate()
    {
        if let Some(attack) = attacks.get(index) {
            values.insert(fields[0].to_owned(), attack.name.clone());
            values.insert(fields[1].to_owned(), signed(attack.attack_bonus));
            values.insert(
                fields[2].to_owned(),
                format!("{} {}", attack.damage, attack.damage_type),
            );
            values.insert(
                fields[3].to_owned(),
                std::iter::once(format!("Range {}", attack.range))
                    .chain(attack.properties.iter().cloned())
                    .chain(attack.notes.iter().cloned())
                    .collect::<Vec<_>>()
                    .join("; "),
            );
        } else {
            for field in fields {
                values.insert((*field).to_owned(), String::new());
            }
        }
    }
    let equipment = character
        .inventory()
        .iter()
        .map(|item| {
            if item.quantity > 1 {
                format!("{} x {}", item.quantity, item.name)
            } else {
                item.name.clone()
            }
        })
        .collect::<Vec<_>>()
        .join("\n");
    values.insert("Text99".to_owned(), equipment);
    let coins = character.coins();
    for (field, amount) in [
        ("Text226", coins.copper),
        ("Text267", coins.silver),
        ("Text268", coins.electrum),
        ("Text269", coins.gold),
        ("Text270", coins.platinum),
    ] {
        values.insert(field.to_owned(), amount.to_string());
    }
    if let Some(profile) = character.spellcasting_profiles().first() {
        values.insert("Text93".to_owned(), signed(profile.modifier));
        values.insert("Text94".to_owned(), profile.save_dc.to_string());
        values.insert("Text95".to_owned(), signed(profile.attack_bonus));
        values.insert("Text111".to_owned(), title_case(&profile.ability));
    }
    for field in [
        "Text112", "Text113", "Text114", "Text117", "Text116", "Text115", "Text118", "Text119",
        "Text120",
    ] {
        values.insert(field.to_owned(), String::new());
    }
    if let Some(slot) = character.spell_slots().first() {
        values.insert("Text112".to_owned(), slot.total.to_string());
    }
    project_spell_rows(character, &mut values);
    render_fields(template, output, &values)
}

fn character_languages(character: &Character) -> Vec<String> {
    let mut languages = vec!["Common".to_owned()];
    languages.extend(character.selected_languages.iter().cloned());
    languages.extend(character.class_choices.additional_language.iter().cloned());
    languages
}

fn character_details(character: &Character) -> String {
    [
        character
            .backstory
            .as_ref()
            .map(|value| format!("Backstory\n{value}")),
        character
            .personality
            .as_ref()
            .map(|value| format!("Personality\n{value}")),
    ]
    .into_iter()
    .flatten()
    .collect::<Vec<_>>()
    .join("\n\n")
}

fn signed(value: i16) -> String {
    format!("{value:+}")
}

fn title_case(value: &str) -> String {
    let mut chars = value.chars();
    chars.next().map_or_else(String::new, |first| {
        first.to_uppercase().collect::<String>() + chars.as_str()
    })
}

/// Compact supported-template identity used by the Rust proof tests.
#[derive(Debug, PartialEq, Eq)]
pub struct TemplateInventory {
    pub page_count: usize,
    pub field_count: usize,
    pub text_field_count: usize,
    pub button_field_count: usize,
    pub untyped_field_count: usize,
    pub sha256: String,
}

/// Enumerate every `AcroForm` field exposed by the page widgets.
///
/// # Errors
///
/// Returns an error when the PDF cannot be read or a page/widget is malformed.
pub fn template_inventory(template: impl AsRef<Path>) -> Result<TemplateInventory> {
    let document = Document::load(template).map_err(|error| error.to_string())?;
    let entries = field_entries(&document)?;
    let mut hasher = Sha256::new();
    let mut text_field_count = 0;
    let mut button_field_count = 0;
    let mut untyped_field_count = 0;
    for (name, kind) in &entries {
        hasher.update(name.as_bytes());
        hasher.update(b"\t");
        hasher.update(kind.as_bytes());
        hasher.update(b"\n");
        match kind.as_str() {
            "/Tx" => text_field_count += 1,
            "/Btn" => button_field_count += 1,
            _ => untyped_field_count += 1,
        }
    }
    let mut sha256 = String::new();
    for byte in hasher.finalize() {
        write!(&mut sha256, "{byte:02x}").expect("writing to a String cannot fail");
    }
    Ok(TemplateInventory {
        page_count: document.get_pages().len(),
        field_count: entries.len(),
        text_field_count,
        button_field_count,
        untyped_field_count,
        sha256,
    })
}

/// Enumerate the root `AcroForm` field tree, including non-widget hierarchy entries.
///
/// # Errors
///
/// Returns an error when the document lacks a readable `AcroForm` field tree.
pub fn acroform_inventory(template: impl AsRef<Path>) -> Result<TemplateInventory> {
    let document = Document::load(template).map_err(|error| error.to_string())?;
    let (_, catalog) = document
        .dereference(
            document
                .trailer
                .get(b"Root")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let catalog = catalog.as_dict().map_err(|error| error.to_string())?;
    let (_, form) = document
        .dereference(
            catalog
                .get(b"AcroForm")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let form = form.as_dict().map_err(|error| error.to_string())?;
    let (_, roots) = document
        .dereference(form.get(b"Fields").map_err(|error| error.to_string())?)
        .map_err(|error| error.to_string())?;
    let mut entries = Vec::new();
    for field in roots.as_array().map_err(|error| error.to_string())? {
        collect_field_entries(&document, field, "", &mut entries)?;
    }
    Ok(inventory_from_entries(document.get_pages().len(), entries))
}

/// Render a precomputed mapping of supported template field names to values.
///
/// Button values use `"/Off"` for unchecked and any other value for checked;
/// the renderer obtains the actual on-state from the widget appearance stream.
///
/// # Errors
///
/// Returns an error when the template is unreadable, a named field is absent, a
/// field has an unsupported type, or the output cannot be written.
pub fn render_fields(
    template: impl AsRef<Path>,
    output: impl AsRef<Path>,
    values: &BTreeMap<String, String>,
) -> Result<()> {
    let mut document = Document::load(template).map_err(|error| error.to_string())?;
    let index = field_index(&document)?;
    for (name, value) in values {
        let (widget, target) = index
            .get(name)
            .copied()
            .ok_or_else(|| format!("field not found: {name}"))?;
        let kind = field_kind(&document, widget, target)?;
        match kind.as_str() {
            "/Tx" => set_text(&mut document, widget, target, value)?,
            "/Btn" => set_checkbox(&mut document, widget, target, value != "/Off")?,
            _ => return Err(format!("unsupported field type for {name}: {kind}")),
        }
    }
    document.save(output).map_err(|error| error.to_string())?;
    Ok(())
}

/// Read the stored field value after reopening a proof output.
///
/// # Errors
///
/// Returns an error when the PDF cannot be read, the field is absent, or it has
/// no stored value.
pub fn read_field_value(path: impl AsRef<Path>, field_name: &str) -> Result<Object> {
    let document = Document::load(path).map_err(|error| error.to_string())?;
    let (_, target) = field_index(&document)?
        .get(field_name)
        .copied()
        .ok_or_else(|| format!("field not found: {field_name}"))?;
    document
        .get_object(target)
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?
        .get(b"V")
        .cloned()
        .map_err(|error| error.to_string())
}

/// Read a set of stored field values with one template traversal.
///
/// # Errors
///
/// Returns an error when the PDF cannot be read or any requested field is absent.
pub fn read_field_values(
    path: impl AsRef<Path>,
    field_names: impl IntoIterator<Item = String>,
) -> Result<BTreeMap<String, Object>> {
    let document = Document::load(path).map_err(|error| error.to_string())?;
    let index = field_index(&document)?;
    field_names
        .into_iter()
        .map(|name| {
            let (_, target) = index
                .get(&name)
                .copied()
                .ok_or_else(|| format!("field not found: {name}"))?;
            let value = document
                .get_object(target)
                .and_then(Object::as_dict)
                .map_err(|error| error.to_string())?
                .get(b"V")
                .cloned()
                .map_err(|error| format!("field {name}: {error}"))?;
            Ok((name, value))
        })
        .collect()
}

fn set_text(
    document: &mut Document,
    widget: ObjectId,
    target: ObjectId,
    value: &str,
) -> Result<()> {
    let appearance = text_appearance(document, widget, target, value)?;
    let field = document
        .get_object_mut(target)
        .and_then(Object::as_dict_mut)
        .map_err(|error| error.to_string())?;
    field.set("V", Object::string_literal(value));
    field.set("DA", Object::string_literal("/Helv 0 Tf 0 g"));
    let widget = document
        .get_object_mut(widget)
        .and_then(Object::as_dict_mut)
        .map_err(|error| error.to_string())?;
    widget.set("DA", Object::string_literal("/Helv 0 Tf 0 g"));
    widget.set(
        "AP",
        Object::Dictionary(dictionary! { "N" => Object::Reference(appearance) }),
    );
    Ok(())
}

fn text_appearance(
    document: &mut Document,
    widget: ObjectId,
    target: ObjectId,
    value: &str,
) -> Result<ObjectId> {
    let widget_dictionary = document
        .get_object(widget)
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    let rectangle = widget_dictionary
        .get(b"Rect")
        .and_then(Object::as_array)
        .map_err(|error| error.to_string())?;
    if rectangle.len() != 4 {
        return Err("text widget rectangle must have four coordinates".to_owned());
    }
    let width = (rectangle[2].as_f32().map_err(|error| error.to_string())?
        - rectangle[0].as_f32().map_err(|error| error.to_string())?)
    .abs();
    let height = (rectangle[3].as_f32().map_err(|error| error.to_string())?
        - rectangle[1].as_f32().map_err(|error| error.to_string())?)
    .abs();
    let flags = document
        .get_object(target)
        .and_then(Object::as_dict)
        .ok()
        .and_then(|field| field.get(b"Ff").ok())
        .or_else(|| widget_dictionary.get(b"Ff").ok())
        .and_then(|flags| flags.as_i64().ok())
        .unwrap_or(0);
    let multiline = flags & 4096 != 0 || value.contains('\n');
    let (font_size, lines) = text_layout(value, width - 4.0, height - 2.0, multiline);
    let leading = font_size * 1.156;
    let initial_y = if multiline {
        height - font_size * 0.85
    } else {
        (height - font_size) * 0.5 + font_size * 0.18
    };
    let mut operations = vec![
        Operation::new("q", vec![]),
        Operation::new("BMC", vec![Object::Name(b"Tx".to_vec())]),
        Operation::new("q", vec![]),
        Operation::new(
            "re",
            vec![
                2.into(),
                1.into(),
                (width - 4.0).into(),
                (height - 2.0).into(),
            ],
        ),
        Operation::new("W", vec![]),
        Operation::new("n", vec![]),
        Operation::new("BT", vec![]),
        Operation::new("Tf", vec![Object::Name(b"Helv".to_vec()), font_size.into()]),
        Operation::new("g", vec![0.into()]),
        Operation::new("Td", vec![2.into(), initial_y.into()]),
    ];
    for (index, line) in lines.iter().enumerate() {
        if index > 0 {
            operations.push(Operation::new("Td", vec![0.into(), (-leading).into()]));
        }
        operations.push(Operation::new(
            "Tj",
            vec![Object::string_literal(appearance_text(line))],
        ));
    }
    operations.extend([
        Operation::new("ET", vec![]),
        Operation::new("Q", vec![]),
        Operation::new("EMC", vec![]),
        Operation::new("Q", vec![]),
    ]);
    let resources = Object::Dictionary(dictionary! {
        "Font" => Object::Dictionary(dictionary! { "Helv" => helvetica_resource(document)? })
    });
    let stream = Stream::new(
        dictionary! {
            "Type" => "XObject",
            "Subtype" => "Form",
            "BBox" => vec![0.into(), 0.into(), width.into(), height.into()],
            "Resources" => resources,
        },
        Content { operations }
            .encode()
            .map_err(|error| error.to_string())?,
    );
    Ok(document.add_object(stream))
}

fn helvetica_resource(document: &Document) -> Result<Object> {
    let (_, catalog) = document
        .dereference(
            document
                .trailer
                .get(b"Root")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let catalog = catalog.as_dict().map_err(|error| error.to_string())?;
    let (_, form) = document
        .dereference(
            catalog
                .get(b"AcroForm")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let form = form.as_dict().map_err(|error| error.to_string())?;
    let (_, resources) = document
        .dereference(form.get(b"DR").map_err(|error| error.to_string())?)
        .map_err(|error| error.to_string())?;
    let resources = resources.as_dict().map_err(|error| error.to_string())?;
    let (_, fonts) = document
        .dereference(resources.get(b"Font").map_err(|error| error.to_string())?)
        .map_err(|error| error.to_string())?;
    fonts
        .as_dict()
        .map_err(|error| error.to_string())?
        .get(b"Helv")
        .cloned()
        .map_err(|error| error.to_string())
}

fn text_layout(value: &str, width: f32, height: f32, multiline: bool) -> (f32, Vec<String>) {
    let normalized = if multiline {
        value.to_owned()
    } else {
        value.replace(['\r', '\n'], " ")
    };
    for half_points in (6_u8..=24).rev() {
        let size = f32::from(half_points) / 2.0;
        let lines = if multiline {
            wrap_text(&normalized, width, size)
        } else {
            vec![normalized.clone()]
        };
        let fits_width = lines
            .iter()
            .all(|line| estimated_text_width(line, size) <= width);
        let fits_height = if multiline {
            f32::from(u16::try_from(lines.len()).unwrap_or(u16::MAX)) * size * 1.156 <= height
        } else {
            size * 1.156 <= height
        };
        if fits_width && fits_height {
            return (size, lines);
        }
    }
    let size = 3.0;
    let lines = if multiline {
        wrap_text(&normalized, width, size)
    } else {
        vec![normalized]
    };
    (size, lines)
}

fn wrap_text(value: &str, width: f32, font_size: f32) -> Vec<String> {
    let mut lines = Vec::new();
    for paragraph in value.replace('\r', "").split('\n') {
        let mut line = String::new();
        for word in paragraph.split_whitespace() {
            let candidate = if line.is_empty() {
                word.to_owned()
            } else {
                format!("{line} {word}")
            };
            if line.is_empty() || estimated_text_width(&candidate, font_size) <= width {
                line = candidate;
            } else {
                lines.push(std::mem::take(&mut line));
                word.clone_into(&mut line);
            }
        }
        lines.push(line);
    }
    if lines.is_empty() {
        lines.push(String::new());
    }
    lines
}

fn estimated_text_width(value: &str, font_size: f32) -> f32 {
    value
        .chars()
        .map(|character| match character {
            'i' | 'l' | 'I' | '!' | '.' | ',' | ':' | ';' | '\'' => 0.25,
            'm' | 'w' | 'M' | 'W' | '@' => 0.85,
            ' ' => 0.28,
            _ => 0.52,
        })
        .sum::<f32>()
        * font_size
}

fn appearance_text(value: &str) -> String {
    value
        .chars()
        .map(
            |character| {
                if character.is_ascii() { character } else { '?' }
            },
        )
        .collect()
}

fn set_checkbox(
    document: &mut Document,
    widget: ObjectId,
    target: ObjectId,
    checked: bool,
) -> Result<()> {
    let state = if checked {
        checkbox_on_state(document, widget)?
    } else {
        b"Off".to_vec()
    };
    document
        .get_object_mut(target)
        .and_then(Object::as_dict_mut)
        .map_err(|error| error.to_string())?
        .set("V", Object::Name(state.clone()));
    document
        .get_object_mut(widget)
        .and_then(Object::as_dict_mut)
        .map_err(|error| error.to_string())?
        .set("AS", Object::Name(state));
    Ok(())
}

fn field_kind(document: &Document, widget: ObjectId, target: ObjectId) -> Result<String> {
    let target = document
        .get_object(target)
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    let widget = document
        .get_object(widget)
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    target
        .get(b"FT")
        .or_else(|_| widget.get(b"FT"))
        .and_then(Object::as_name)
        .map(|value| format!("/{}", String::from_utf8_lossy(value)))
        .map_err(|error| error.to_string())
}

fn checkbox_on_state(document: &Document, widget: ObjectId) -> Result<Vec<u8>> {
    let widget = document
        .get_object(widget)
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    let appearance = widget
        .get(b"AP")
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    let normal = appearance
        .get(b"N")
        .and_then(Object::as_dict)
        .map_err(|error| error.to_string())?;
    normal
        .iter()
        .find_map(|(name, _)| (name.as_slice() != b"Off").then(|| name.clone()))
        .ok_or_else(|| "checkbox has no on-state appearance".to_owned())
}

fn field_index(document: &Document) -> Result<BTreeMap<String, (ObjectId, ObjectId)>> {
    let paths = acroform_path_index(document)?;
    let mut index = BTreeMap::new();
    for (widget, target, name, _) in field_entries_with_ids(document)? {
        let path = paths.get(&target).cloned().unwrap_or(name.clone());
        let candidate = if name == path
            || name.is_empty()
            || path
                .rsplit('.')
                .next()
                .is_some_and(|segment| segment == name)
        {
            path
        } else {
            format!("{path}.{name}")
        };
        index.insert(candidate, (widget, target));
        index.insert(name, (widget, target));
    }
    Ok(index)
}

fn acroform_path_index(document: &Document) -> Result<BTreeMap<ObjectId, String>> {
    let (_, catalog) = document
        .dereference(
            document
                .trailer
                .get(b"Root")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let catalog = catalog.as_dict().map_err(|error| error.to_string())?;
    let (_, form) = document
        .dereference(
            catalog
                .get(b"AcroForm")
                .map_err(|error| error.to_string())?,
        )
        .map_err(|error| error.to_string())?;
    let form = form.as_dict().map_err(|error| error.to_string())?;
    let (_, roots) = document
        .dereference(form.get(b"Fields").map_err(|error| error.to_string())?)
        .map_err(|error| error.to_string())?;
    let mut index = BTreeMap::new();
    for field in roots.as_array().map_err(|error| error.to_string())? {
        collect_field_paths(document, field, "", &mut index)?;
    }
    Ok(index)
}

fn collect_field_paths(
    document: &Document,
    field: &Object,
    parent_name: &str,
    index: &mut BTreeMap<ObjectId, String>,
) -> Result<()> {
    let (id, field) = document
        .dereference(field)
        .map_err(|error| error.to_string())?;
    let field = field.as_dict().map_err(|error| error.to_string())?;
    let full_name = if let Ok(name) = field.get(b"T").and_then(Object::as_str) {
        let name = String::from_utf8_lossy(name);
        if parent_name.is_empty() {
            name.into_owned()
        } else {
            format!("{parent_name}.{name}")
        }
    } else {
        parent_name.to_owned()
    };
    if let Some(id) = id {
        index.insert(id, full_name.clone());
    }
    if let Ok(kids) = field.get(b"Kids") {
        let (_, kids) = document
            .dereference(kids)
            .map_err(|error| error.to_string())?;
        for child in kids.as_array().map_err(|error| error.to_string())? {
            collect_field_paths(document, child, &full_name, index)?;
        }
    }
    Ok(())
}

fn field_entries(document: &Document) -> Result<Vec<(String, String)>> {
    let mut entries = field_entries_with_ids(document)?
        .into_iter()
        .map(|(_, target, name, kind)| {
            let target_name = document
                .get_object(target)
                .and_then(Object::as_dict)
                .ok()
                .and_then(|field| field.get(b"T").ok())
                .and_then(|value| value.as_str().ok())
                .map_or(name, |value| String::from_utf8_lossy(value).into_owned());
            (target_name, kind)
        })
        .collect::<Vec<_>>();
    entries.sort_unstable();
    entries.dedup();
    Ok(entries)
}

fn inventory_from_entries(
    page_count: usize,
    mut entries: Vec<(String, String)>,
) -> TemplateInventory {
    entries.sort_unstable();
    entries.dedup();
    let mut hasher = Sha256::new();
    let mut text_field_count = 0;
    let mut button_field_count = 0;
    let mut untyped_field_count = 0;
    for (name, kind) in &entries {
        hasher.update(name.as_bytes());
        hasher.update(b"\t");
        hasher.update(kind.as_bytes());
        hasher.update(b"\n");
        match kind.as_str() {
            "/Tx" => text_field_count += 1,
            "/Btn" => button_field_count += 1,
            _ => untyped_field_count += 1,
        }
    }
    let mut sha256 = String::new();
    for byte in hasher.finalize() {
        write!(&mut sha256, "{byte:02x}").expect("writing to a String cannot fail");
    }
    TemplateInventory {
        page_count,
        field_count: entries.len(),
        text_field_count,
        button_field_count,
        untyped_field_count,
        sha256,
    }
}

fn collect_field_entries(
    document: &Document,
    field: &Object,
    parent_name: &str,
    entries: &mut Vec<(String, String)>,
) -> Result<()> {
    let (_, field) = document
        .dereference(field)
        .map_err(|error| error.to_string())?;
    let field = field.as_dict().map_err(|error| error.to_string())?;
    let full_name = if let Ok(name) = field.get(b"T").and_then(Object::as_str) {
        let name = String::from_utf8_lossy(name);
        let full_name = if parent_name.is_empty() {
            name.into_owned()
        } else {
            format!("{parent_name}.{name}")
        };
        let kind = field
            .get(b"FT")
            .ok()
            .and_then(|value| value.as_name().ok())
            .map_or_else(
                || "None".to_owned(),
                |value| format!("/{}", String::from_utf8_lossy(value)),
            );
        entries.push((full_name.clone(), kind));
        full_name
    } else {
        parent_name.to_owned()
    };
    if let Ok(kids) = field.get(b"Kids") {
        let (_, kids) = document
            .dereference(kids)
            .map_err(|error| error.to_string())?;
        for child in kids.as_array().map_err(|error| error.to_string())? {
            collect_field_entries(document, child, &full_name, entries)?;
        }
    }
    Ok(())
}

fn field_entries_with_ids(
    document: &Document,
) -> Result<Vec<(ObjectId, ObjectId, String, String)>> {
    let mut entries = Vec::new();
    for page_id in document.get_pages().into_values() {
        let page = document
            .get_object(page_id)
            .and_then(Object::as_dict)
            .map_err(|error| error.to_string())?;
        let (_, annotations) = document
            .dereference(page.get(b"Annots").map_err(|error| error.to_string())?)
            .map_err(|error| error.to_string())?;
        let annotations = annotations.as_array().map_err(|error| error.to_string())?;
        for annotation in annotations {
            let widget_id = annotation
                .as_reference()
                .map_err(|error| error.to_string())?;
            let widget = document
                .get_object(widget_id)
                .and_then(Object::as_dict)
                .map_err(|error| error.to_string())?;
            let target = if widget.get(b"T").is_ok() {
                widget_id
            } else {
                widget
                    .get(b"Parent")
                    .ok()
                    .and_then(|parent| parent.as_reference().ok())
                    .unwrap_or(widget_id)
            };
            let field = document
                .get_object(target)
                .and_then(Object::as_dict)
                .map_err(|error| error.to_string())?;
            let name = widget
                .get(b"T")
                .or_else(|_| field.get(b"T"))
                .and_then(Object::as_str)
                .map_err(|error| error.to_string())?;
            let kind = field
                .get(b"FT")
                .or_else(|_| widget.get(b"FT"))
                .ok()
                .and_then(|value| value.as_name().ok())
                .map_or_else(
                    || "None".to_owned(),
                    |value| format!("/{}", String::from_utf8_lossy(value)),
                );
            entries.push((
                widget_id,
                target,
                String::from_utf8_lossy(name).into_owned(),
                kind,
            ));
        }
    }
    Ok(entries)
}
