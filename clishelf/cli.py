# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import subprocess
import sys
from typing import NoReturn

import click

from .git import cli_git
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


def main() -> NoReturn:
    cli.add_command(cli_git)
    cli.add_command(cli_vs)
    cli.main()


if __name__ == "__main__":
    main()
