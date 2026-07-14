from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pc_wizard.models import Character
from pc_wizard.pdf import render_character_sheet, validate_template
from pc_wizard.wizard import DraftSaved, run_wizard

app = typer.Typer(help="Create D&D characters using SRD 5.2.1.", no_args_is_help=True)
console = Console()


def _validation_details(error: ValidationError) -> str:
    details: list[str] = []
    for item in error.errors(include_url=False):
        location = ".".join(str(part) for part in item["loc"]) or "character"
        details.append(f"{location}: {item['msg']}")
    return "; ".join(details)


def load_character(path: Path) -> Character:
    if not path.is_file():
        raise ValueError(f"character JSON does not exist or is not a file: {path}")
    try:
        return Character.load_json(path)
    except ValidationError as error:
        raise ValueError(f"invalid character JSON {path}: {_validation_details(error)}") from error
    except ValueError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error


def confirm_overwrite(paths: list[Path], force: bool) -> None:
    existing = list(dict.fromkeys(path for path in paths if path.exists()))
    if not existing or force:
        return
    names = ", ".join(str(path) for path in existing)
    if not typer.confirm(f"Overwrite existing output(s): {names}?", default=False):
        raise typer.Abort


def character_table(character: Character) -> Table:
    derived = character.derived_values
    table = Table(title=character.name, show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    rows = (
        ("Identity", f"Level {character.level} {character.species} {character.character_class}"),
        ("Background", character.background),
        ("Alignment", character.alignment),
        (
            "Combat",
            f"HP {derived.hit_points} · AC {derived.armor_class} · Speed {derived.speed} ft.",
        ),
        ("Skills", ", ".join(derived.skills)),
        ("Languages", ", ".join(derived.languages)),
        ("Equipment", ", ".join(item.name for item in derived.equipment) or "None"),
    )
    for label, value in rows:
        table.add_row(label, value)
    return table


def version_callback(value: bool) -> None:
    """Print the installed package version and exit."""
    if value:
        typer.echo(f"pc-wizard {version('pc-wizard')}")
        raise typer.Exit


@app.callback()
def main(
    version_requested: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
) -> None:
    """Create D&D characters using SRD 5.2.1."""


@app.command()
def create(
    template: Annotated[
        Path, typer.Option("--template", help="Official fillable character-sheet PDF.")
    ],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Output character-sheet PDF.")
    ] = Path("character-sheet-filled.pdf"),
    json_output: Annotated[Path, typer.Option("--json", help="Output character JSON.")] = Path(
        "character.json"
    ),
    from_json: Annotated[
        Path | None,
        typer.Option("--from-json", help="Create non-interactively from complete character JSON."),
    ] = None,
    draft: Annotated[
        Path, typer.Option("--draft", help="Incomplete-session checkpoint file.")
    ] = Path("character-draft.json"),
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite existing outputs without confirmation.")
    ] = False,
) -> None:
    """Create a character interactively or from complete JSON."""
    try:
        validate_template(template)
        confirm_overwrite([output, json_output], force)
        character = load_character(from_json) if from_json is not None else run_wizard(draft)
        character.save_json(json_output)
        render_character_sheet(character, template, output)
        if from_json is None:
            draft.unlink(missing_ok=True)
    except DraftSaved:
        console.print(f"[yellow]Creation saved in {draft}.[/yellow]")
        return
    except KeyboardInterrupt:
        message = (
            f"Character creation paused. Resume from {draft}."
            if draft.exists()
            else "Character creation cancelled before the first checkpoint."
        )
        console.print(f"\n[yellow]{message}[/yellow]")
        raise typer.Exit(130) from None
    except (OSError, ValueError, ValidationError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1) from error
    console.print(
        Panel.fit(
            f"[bold green]{character.name} is ready![/bold green]"
            f"\nPDF: {output}\nJSON: {json_output}"
        )
    )


@app.command()
def show(
    character_file: Annotated[Path, typer.Argument(help="Complete current-schema character JSON.")],
) -> None:
    """Show selected and derived character values."""
    try:
        character = load_character(character_file)
    except (OSError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1) from error
    console.print(character_table(character))
