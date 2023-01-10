from json import dumps
from logging import info
from pathlib import Path
from typing import Any

from typer import confirm, echo


def export_to_file(filepath: Path, output: str, override: bool) -> None:
    """
    Check if file already exists
    :param filepath:
    :param output:
    :param override:
    :return:
    """

    if filepath.exists() and not override:
        override_existing = confirm(str(filepath) + " already exists. Override?")
        if not override_existing:
            echo("Aborting.")
            return
    # Write ACTS file to disk
    filepath.write_text(output)

    info("Saved output to " + str(filepath))


def export_to_json(filepath: Path, output_json: Any, override: bool) -> None:
    """
    Export to JSON.
    :param filepath:
    :param output_json:
    :param override:
    :return:
    """
    if filepath.exists() and not override:
        override_existing = confirm(str(filepath) + " already exists. Override?")
        if not override_existing:
            echo("Aborting.")
            return
    filepath.write_text(dumps(output_json, ensure_ascii=False, indent=4))
    echo(f"Saved output to {filepath}")
