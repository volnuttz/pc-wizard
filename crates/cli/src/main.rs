//! Native pc-wizard command-line entry point.

use std::{
    collections::BTreeMap,
    env, fs,
    io::{self, Write as _},
    path::{Path, PathBuf},
    process::ExitCode,
};

use pc_wizard_domain::Character;

const HELP: &str = "Create D&D characters using SRD 5.2.1.

Usage: pc-wizard [OPTIONS] <COMMAND>

Commands:
  create  Create a character interactively or from complete JSON
  validate  Validate a canonical character JSON file
  show    Show selected and derived character values
  help    Print this message or the help of a command

Options:
      --version  Show the version and exit
  -h, --help     Print help
";

fn main() -> ExitCode {
    let arguments: Vec<String> = env::args().skip(1).collect();
    match run(&arguments) {
        Ok(()) => ExitCode::SUCCESS,
        Err((code, message)) => {
            println!("Error: {message}");
            ExitCode::from(code)
        }
    }
}

type CliResult = Result<(), (u8, String)>;

fn run(arguments: &[String]) -> CliResult {
    match arguments.first().map(String::as_str) {
        None | Some("--help" | "-h" | "help") => {
            print!("{HELP}");
            Ok(())
        }
        Some("--version") => {
            println!("pc-wizard {}", env!("CARGO_PKG_VERSION"));
            Ok(())
        }
        Some("validate") => validate(&arguments[1..]),
        Some("show") => show(&arguments[1..]),
        Some("create") => create(&arguments[1..]),
        Some(command) => Err((2, format!("unknown command: {command}\n\n{HELP}"))),
    }
}

fn validate(arguments: &[String]) -> CliResult {
    if arguments == ["--help"] || arguments == ["-h"] {
        println!(
            "Validate a canonical character JSON file.\n\nUsage: pc-wizard validate CHARACTER_JSON"
        );
        return Ok(());
    }
    let [path] = arguments else {
        return Err((2, "Usage: pc-wizard validate CHARACTER_JSON".to_owned()));
    };
    let character = load_character(Path::new(path))?;
    println!("{} is valid.", character.name);
    Ok(())
}

fn show(arguments: &[String]) -> CliResult {
    if arguments == ["--help"] || arguments == ["-h"] {
        println!(
            "Show selected and derived character values.\n\nUsage: pc-wizard show CHARACTER_JSON"
        );
        return Ok(());
    }
    let [path] = arguments else {
        return Err((2, "Usage: pc-wizard show CHARACTER_JSON".to_owned()));
    };
    let character = load_character(Path::new(path))?;
    println!("{}", character.name);
    println!(
        "Identity      Level {} {} {}",
        character.level, character.species, character.character_class
    );
    println!("Background    {}", character.background);
    println!("Alignment     {}", character.alignment);
    println!(
        "Combat        HP {} · AC {} · Speed {} ft.",
        character.hit_points(),
        character.armor_class(),
        character.speed()
    );
    println!(
        "Skills        {}",
        character
            .skills()
            .into_iter()
            .collect::<Vec<_>>()
            .join(", ")
    );
    println!("Languages     {}", languages(&character).join(", "));
    Ok(())
}

fn create(arguments: &[String]) -> CliResult {
    if arguments == ["--help"] || arguments == ["-h"] {
        println!(
            "Create a character interactively or from complete JSON.\n\nUsage: pc-wizard create --template TEMPLATE [--from-json INPUT] [--json JSON] [--output PDF] [--draft DRAFT] [--force]"
        );
        return Ok(());
    }
    let (options, force) = parse_options(arguments)?;
    let template = required_option(&options, "--template")?;
    pc_wizard_pdf_renderer::validate_template(template).map_err(|error| (1, error))?;

    let json_output = PathBuf::from(
        options
            .get("--json")
            .map_or("character.json", String::as_str),
    );
    let pdf_output = PathBuf::from(
        options
            .get("--output")
            .map_or("character-sheet-filled.pdf", String::as_str),
    );
    confirm_overwrite(&[&json_output, &pdf_output], force)?;

    let mut completed_draft = None;
    let character = if let Some(source) = options.get("--from-json") {
        load_character(Path::new(source))?
    } else {
        let draft = PathBuf::from(
            options
                .get("--draft")
                .map_or("character-draft.json", String::as_str),
        );
        println!(
            "Progress is checkpointed in {}; Ctrl-C keeps the latest completed stage.",
            draft.display()
        );
        match pc_wizard_creation::run_interactive(&draft) {
            Ok(character) => {
                completed_draft = Some(draft);
                character
            }
            Err(error) if error == "creation saved for later review" => {
                println!("Creation saved in {}.", draft.display());
                return Ok(());
            }
            Err(error) => return Err((1, error)),
        }
    };
    create_parent(&json_output)?;
    create_parent(&pdf_output)?;
    fs::write(
        &json_output,
        character.to_json().map_err(|error| (1, error))?,
    )
    .map_err(|error| {
        (
            1,
            format!("unable to write {}: {error}", json_output.display()),
        )
    })?;
    if let Err(error) = pc_wizard_pdf_renderer::render_character(&character, template, &pdf_output)
    {
        let _ = fs::remove_file(&json_output);
        return Err((1, error));
    }
    println!("{} is ready!", character.name);
    println!("PDF: {}", pdf_output.display());
    println!("JSON: {}", json_output.display());
    if let Some(draft) = completed_draft {
        let _ = fs::remove_file(draft);
    }
    Ok(())
}

fn parse_options(arguments: &[String]) -> Result<(BTreeMap<String, String>, bool), (u8, String)> {
    let mut options = BTreeMap::new();
    let mut force = false;
    let mut index = 0;
    while index < arguments.len() {
        let option = arguments[index].as_str();
        if option == "--force" {
            force = true;
            index += 1;
            continue;
        }
        let canonical = match option {
            "-o" => "--output",
            "--template" | "--output" | "--json" | "--from-json" | "--draft" => option,
            _ => return Err((2, format!("unknown option: {option}"))),
        };
        let value = arguments
            .get(index + 1)
            .ok_or_else(|| (2, format!("missing value for {option}")))?;
        options.insert(canonical.to_owned(), value.clone());
        index += 2;
    }
    Ok((options, force))
}

fn required_option<'a>(
    options: &'a BTreeMap<String, String>,
    name: &str,
) -> Result<&'a Path, (u8, String)> {
    options
        .get(name)
        .map(Path::new)
        .ok_or_else(|| (2, format!("missing required option {name}")))
}

fn load_character(path: &Path) -> Result<Character, (u8, String)> {
    if !path.is_file() {
        return Err((
            1,
            format!(
                "character JSON does not exist or is not a file: {}",
                path.display()
            ),
        ));
    }
    let source = fs::read_to_string(path)
        .map_err(|error| (1, format!("unable to read {}: {error}", path.display())))?;
    Character::from_json(&source).map_err(|error| {
        (
            1,
            format!("invalid character JSON {}: {error}", path.display()),
        )
    })
}

fn confirm_overwrite(paths: &[&Path], force: bool) -> CliResult {
    let existing: Vec<String> = paths
        .iter()
        .filter(|path| path.exists())
        .map(|path| path.display().to_string())
        .collect();
    if existing.is_empty() || force {
        return Ok(());
    }
    print!(
        "Overwrite existing output(s): {}? [y/N] ",
        existing.join(", ")
    );
    io::stdout()
        .flush()
        .map_err(|error| (1, error.to_string()))?;
    let mut answer = String::new();
    io::stdin()
        .read_line(&mut answer)
        .map_err(|error| (1, error.to_string()))?;
    if matches!(answer.trim().to_ascii_lowercase().as_str(), "y" | "yes") {
        Ok(())
    } else {
        Err((1, "Aborted".to_owned()))
    }
}

fn create_parent(path: &Path) -> CliResult {
    if let Some(parent) = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
    {
        fs::create_dir_all(parent)
            .map_err(|error| (1, format!("unable to create {}: {error}", parent.display())))?;
    }
    Ok(())
}

fn languages(character: &Character) -> Vec<String> {
    let mut values = vec!["Common".to_owned()];
    values.extend(character.selected_languages.iter().cloned());
    values.extend(character.class_choices.additional_language.iter().cloned());
    values
}

#[cfg(test)]
mod tests {
    use super::run;

    #[test]
    fn help_and_version_succeed() {
        assert_eq!(run(&["--help".to_owned()]), Ok(()));
        assert_eq!(run(&["--version".to_owned()]), Ok(()));
    }
}
