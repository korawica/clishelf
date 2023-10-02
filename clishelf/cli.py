# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import subprocess
import sys

import click

from .git import cli_git
from .version import cli_vs


@click.group()
def cli():
    """A simple command line tool."""
    pass  # pragma: no cover.


@cli.command()
def echo():
    """Echo Hello World"""
    print("Hello World")
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
)
def cove(module: str, html: bool):
    """Run coverage"""
    subprocess.run(["coverage", "run", "--m", module, "tests"])
    subprocess.run(["coverage", "combine"])
    subprocess.run(["coverage", "report", "--show-missing"])
    if html:
        subprocess.run(["coverage", "html"])


def main() -> None:
    cli.add_command(cli_git)
    cli.add_command(cli_vs)
    cli.main()


if __name__ == "__main__":
    main()
