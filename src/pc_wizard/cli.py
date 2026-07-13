from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from pc_wizard.models import Character
from pc_wizard.pdf import render_character_sheet, validate_template
from pc_wizard.wizard import run_wizard

app = typer.Typer(help="Create D&D characters using SRD 5.2.1.", no_args_is_help=True)
console = Console()


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
) -> None:
    """Run the step-by-step character creation wizard."""
    try:
        validate_template(template)
        character = run_wizard()
        character.save_json(json_output)
        render_character_sheet(character, template, output)
    except KeyboardInterrupt:
        console.print("\n[yellow]Character creation cancelled.[/yellow]")
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
def render(
    character_file: Annotated[Path, typer.Argument(help="Character JSON created by pc-wizard.")],
    template: Annotated[
        Path, typer.Option("--template", help="Official fillable character-sheet PDF.")
    ],
    output: Annotated[Path, typer.Option("--output", "-o")] = Path("character-sheet-filled.pdf"),
) -> None:
    """Render a saved character JSON into the PDF template."""
    try:
        validate_template(template)
        character = Character.load_json(character_file)
        render_character_sheet(character, template, output)
    except (OSError, ValueError, ValidationError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1) from error
    console.print(f"[green]Created {output}[/green]")
