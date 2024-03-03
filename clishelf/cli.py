# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
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
    pass  # pragma: no cover.


@cli.command()
def echo():
    """Echo Hello World"""
    click.echo("Hello World", file=sys.stdout)
    sys.exit(0)


@cli.command()
def conf():
    """Return config for clishelf commands"""
    click.echo(json.dumps(load_config(), indent=4))
    sys.exit(0)


@cli.command()
@click.option(
    "-m",
    "--module",
    type=click.STRING,
    default="pytest",
)
@click.option(
    "-h",
    "--html",
    is_flag=True,
    help="If True, it will generate coverage html file on `htmlcov/`.",
)
def cove(module: str, html: bool):
    """Run the coverage command."""
    subprocess.run(["coverage", "run", "--m", module, "tests"])
    subprocess.run(
        ["coverage", "combine"],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(["coverage", "report", "--show-missing"])
    if html:
        subprocess.run(["coverage", "html"])
    sys.exit(0)


@cli.command()
@click.option(
    "-f",
    "--output-file",
    type=click.STRING,
    default=None,
    help="An output file that want to export the dependencies.",
)
@click.option(
    "-o",
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
            f"./{output_file}" if (x == project and output_file) else x
            for x in (
                load_pyproject()
                .get("project", {})
                .get("optional-dependencies", {})
                .get(optional, [])
            )
        ]

    for d in deps:
        click.echo(d)

    for d in optional_deps:
        if output_file and d == f"./{output_file}":
            continue
        click.echo(d)

    if output_file:
        with pathlib.Path(f"./{output_file}").open(
            mode="wt", encoding="utf-8"
        ) as f:
            f.write("\n".join(deps))

        if optional:
            fn, ext = output_file.split(".", maxsplit=1)
            with pathlib.Path(f"./{fn}.{optional}.{ext}").open(
                mode="wt", encoding="utf-8"
            ) as f:
                f.write("\n".join(optional_deps))


def main() -> NoReturn:
    cli.add_command(cli_git)
    cli.add_command(cli_vs)
    cli.add_command(cli_emoji)
    cli.main()


if __name__ == "__main__":
    main()
