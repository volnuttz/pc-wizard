use std::collections::BTreeSet;

use inquire::{MultiSelect, Select, Text};

use crate::{Result, WizardError, choice_description};

pub(crate) fn prompt(label: &str) -> Result<String> {
    Text::new(label)
        .with_help_message("Press Esc to return to the previous step.")
        .prompt()
        .map_err(|_| WizardError::Back)
}

pub(crate) fn optional_prompt(label: &str) -> Result<Option<String>> {
    Text::new(&format!("{label} (optional)"))
        .with_help_message("Leave blank to skip; press Esc to return to the previous step.")
        .prompt()
        .map(|value| (!value.is_empty()).then_some(value))
        .map_err(|_| WizardError::Back)
}

pub(crate) fn choose(label: &str, choices: &[&str]) -> Result<String> {
    Select::new(label, options(choices, true))
        .with_help_message("Type to filter; Enter selects; Esc goes back.")
        .prompt()
        .map(|choice| choice.value)
        .map_err(|_| WizardError::Back)
}

pub(crate) fn choose_set(label: &str, choices: &[&str], count: usize) -> Result<BTreeSet<String>> {
    choose_set_with_descriptions(label, choices, count, true)
}

pub(crate) fn choose_set_with_descriptions(
    label: &str,
    choices: &[&str],
    count: usize,
    descriptions: bool,
) -> Result<BTreeSet<String>> {
    loop {
        let selected = MultiSelect::new(label, options(choices, descriptions))
            .prompt()
            .map_err(|_| WizardError::Back)?;
        if selected.len() == count {
            return Ok(selected.into_iter().map(|choice| choice.value).collect());
        }
        println!(
            "Select exactly {count} option(s); you selected {}.",
            selected.len()
        );
    }
}

#[derive(Clone)]
struct OptionLabel {
    value: String,
    label: String,
}
impl std::fmt::Display for OptionLabel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.label.fmt(f)
    }
}
fn options(choices: &[&str], descriptions: bool) -> Vec<OptionLabel> {
    choices
        .iter()
        .map(|choice| OptionLabel {
            value: (*choice).to_owned(),
            label: if descriptions {
                choice_description(choice).map_or_else(
                    || (*choice).to_owned(),
                    |description| format!("{choice} — {description}"),
                )
            } else {
                (*choice).to_owned()
            },
        })
        .collect()
}
