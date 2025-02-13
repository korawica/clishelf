# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn, Optional

import click

from .emoji import cli_emoji
from .git import cli_git
from .utils import load_config
from .version import cli_vs

cli: click.Command


@click.group()
def cli():
    """The Main Shelf commands."""
    pass  # pragma: no cov


@cli.command()
def conf():
    """Return a config data of clishelf engine that load from local yaml or toml
    file.
    """
    click.echo(json.dumps(load_config(), indent=4))
    sys.exit(0)


@cli.command()
@click.option(
    "-m",
    "--module",
    type=click.STRING,
    default="pytest",
    help="A module engine that want to pass to coverage (default be `pytest`).",
)
@click.option(
    "-h",
    "--html",
    is_flag=True,
    help="If True, it will generate coverage html file at `./htmlcov/`.",
)
def cove(module: str, html: bool):
    """Run the coverage command."""
    try:
        _ = __import__("coverage")
    except ImportError:
        raise ImportError(  # no cove
            "Please install `coverage` package before using the cove cmd by "
            "`pip install -U coverage`."
        ) from None

    subprocess.run(["coverage", "run", "--m", module, "tests"])
    subprocess.run(
        ["coverage", "combine"],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(["coverage", "report", "--show-missing"])

    # NOTE: Generate html if flag is passing.
    if html:
        subprocess.run(["coverage", "html"])

    sys.exit(0)


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.STRING,
    default=None,
    help="An output file that want to export the dependencies.",
)
@click.option(
    "--optional",
    type=click.STRING,
    default=None,
    help="An optional dependencies string if this project was set.",
)
def dep(
    output_file: Optional[str] = None,
    optional: Optional[str] = None,
) -> NoReturn:
    """List of Dependencies that was set in pyproject.toml file."""
    from .utils import load_pyproject

    project: str = load_pyproject().get("project", {}).get("name", "unknown")
    deps: list[str] = (
        load_pyproject().get("project", {}).get("dependencies", [])
    )

    optional_deps: list[str] = []
    if optional:
        optional_deps = [
            f"-r ./{output_file}" if (x == project and output_file) else x
            for x in (
                load_pyproject()
                .get("project", {})
                .get("optional-dependencies", {})
                .get(optional, [])
            )
        ]

    # NOTE: Echo the project dependencies.
    for d in deps:
        click.echo(d)

    for d in optional_deps:
        if output_file and d == f"-r ./{output_file}":
            continue
        click.echo(d)

    # NOTE: Start writing file.
    if output_file:
        with Path(f"./{output_file}").open(mode="wt", encoding="utf-8") as f:
            f.write("\n".join(deps))

        if optional:
            # NOTE: Split stem and filename.
            fn, ext = output_file.split(".", maxsplit=1)

            file_optional: str = f"./{fn}.{optional}.{ext}"
            with Path(file_optional).open(mode="wt", encoding="utf-8") as f:
                f.write("\n".join(optional_deps))


def main() -> NoReturn:
    """Make cli main object."""
    cli.add_command(cli_git)
    cli.add_command(cli_vs)
    cli.add_command(cli_emoji)
    cli.main()


if __name__ == "__main__":
    main()
