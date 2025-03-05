# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
import re
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
    """Run the coverage command.

    \f
    :param module:
    :param html:
    """
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


def get_dep_optional(
    project: str,
    optional: str,
    project_deps_optional: dict[str, list],
) -> list[str]:  # pragma: no cov
    rs: list[str] = []
    rs_clear: list[str] = []
    if optional not in project_deps_optional:
        raise ValueError(f"Optional dependency {optional!r} does not exists.")

    for x in project_deps_optional.get(optional, []):
        if x.startswith(project):
            op: Optional[re.Match[str]] = re.search(
                rf"{project}(?:\[(?P<optionals>[\w,]+)])?", x
            )
            if op is None:
                raise ValueError(
                    f"The format of nested dependency {x!r} does not valid."
                )

            for o in op.groupdict()["optionals"].split(","):
                rs.extend(get_dep_optional(project, o, project_deps_optional))
        else:
            rs.append(x)

    # NOTE: Clear duplicate with order packages.
    for i in rs:
        if i not in rs_clear:
            rs_clear.append(i)

    return rs_clear


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
    output: Optional[str] = None,
    optional: Optional[str] = None,
) -> NoReturn:
    """List of Dependencies that was set in pyproject.toml file.

    \f
    :param output:
    :param optional:
    """
    from .utils import load_pyproject

    project: str = load_pyproject().get("project", {}).get("name", "unknown")
    project_deps: list[str] = (
        load_pyproject().get("project", {}).get("dependencies", [])
    )

    optional_deps: list[str] = []
    if optional:
        optional_deps = get_dep_optional(
            project,
            optional=optional,
            project_deps_optional=(
                load_pyproject()
                .get("project", {})
                .get("optional-dependencies", {})
            ),
        )

    # NOTE: Echo the project dependencies.
    for d in project_deps + optional_deps:
        click.echo(d)

    # NOTE: Start writing file.
    if output:
        with Path(f"./{output}").open(mode="wt", encoding="utf-8") as f:
            f.write("\n".join(project_deps))
            f.write("\n")

            if optional:
                f.write("# Optional deps\n")
                f.write("\n".join(optional_deps))
                f.write("\n")


def main() -> NoReturn:
    """Make cli main object."""
    cli.add_command(cli_git)
    cli.add_command(cli_vs)
    cli.add_command(cli_emoji)
    cli.main()


if __name__ == "__main__":
    main()
