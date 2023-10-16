# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple

import click

from .git import CommitLog, get_latest_tag
from .settings import BumpVerConf

BUMP_VERSION: Tuple[Tuple[str, str], ...] = (
    ("bump", ":bookmark:"),  # 🔖 :bookmark:
)

cli_vs: click.Command
GroupCommitLog = Dict[str, List[CommitLog]]


def gen_group_commit_log() -> GroupCommitLog:
    """Generate Group of the Commit Logs

    :rtype: GroupCommitLog
    """
    from .git import get_commit_logs

    group_logs: GroupCommitLog = defaultdict(list)
    for log in get_commit_logs(
        excluded=[
            r"pre-commit autoupdate",
            r"^Merge",
        ]
    ):
        group_logs[log.msg.mtype].append(log)
    return {
        k: sorted(v, key=lambda x: x.date, reverse=True)
        for k, v in group_logs.items()
    }


# TODO: add new style of changelog file
# TODO: add parameter that able to write after release version like
#  hot-changes commit
def writer_changelog(file: str):
    """Write Commit logs to the changelog file."""
    group_logs: GroupCommitLog = gen_group_commit_log()

    with Path(file).open(encoding="utf-8") as f_changes:
        changes = f_changes.read().splitlines()

    writer = Path(file).open(mode="w", encoding="utf-8", newline="")
    skip_line: bool = True
    written: bool = False
    for line in changes:
        if line.startswith("## Latest Changes"):
            skip_line = False

        if m := re.match(rf"##\s({BumpVerConf.regex})", line):
            if not written:
                writer.write(f"## Latest Changes{os.linesep}{os.linesep}")
                written = True
            if f"v{m.group(1)}" == get_latest_tag():
                skip_line = True

        if skip_line:
            writer.write(line + os.linesep)
        elif written:
            continue
        else:
            write_group_log(writer, group_logs)
            written = True
    writer.close()


def write_group_log(writer, group_logs):
    from .git import COMMIT_PREFIX_TYPE

    linesep = os.linesep
    if any(cpt[0] in group_logs for cpt in COMMIT_PREFIX_TYPE):
        linesep = f"{os.linesep}{os.linesep}"

    writer.write(f"## Latest Changes{linesep}")

    for cpt in COMMIT_PREFIX_TYPE:
        if cpt[0] in group_logs:
            writer.write(f"### {cpt[0]}{os.linesep}{os.linesep}")
            for log in group_logs[cpt[0]]:
                writer.write(
                    f"- {log.msg.content} (_{log.date:%Y-%m-%d}_)"
                    f"{os.linesep}"
                )
            writer.write(os.linesep)


def write_bump_file(
    file: str,
    changelog_file: str,
    *,
    version: int = 1,
) -> NoReturn:
    with Path(".bumpversion.cfg").open(mode="w", encoding="utf-8") as f_bump:
        f_bump.write(
            getattr(BumpVerConf, f"v{version}").format(
                file=file,
                changelog=changelog_file,
                main=BumpVerConf.main.format(
                    version=current_version(file),
                    msg=BumpVerConf.msg,
                    regex=BumpVerConf.regex,
                ),
            )
        )


def bump2version(
    action: str,
    file: str,
    changelog_file: str,
    ignore_changelog: bool = False,
    dry_run: bool = False,
    version: int = 1,
):
    """Bump version process."""
    # Start writing ``.bump2version.cfg`` file on current path.
    write_bump_file(file, changelog_file, version=version)

    if not ignore_changelog:
        writer_changelog(file=changelog_file)

    # COMMIT: commit add config and edit changelog file.
    subprocess.run(["git", "add", "-A"])
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "build: add bump2version config file",
            "--no-verify",
        ],
        stdout=subprocess.DEVNULL,
    )
    click.echo("Start write '.bump2version.cfg' config file ...")
    subprocess.run(
        [
            "bump2version",
            action,
            "--commit-args=--no-verify",
        ]
        + (["--list", "--dry-run"] if dry_run else [])
    )

    subprocess.run(
        [
            "git",
            "reset",
            "--soft",
            "HEAD~1",
        ],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )

    # Remove ``.bump2version.cfg`` file.
    Path(".bumpversion.cfg").unlink(missing_ok=False)
    click.echo("Unlink '.bump2version.cfg' config file ...")

    with Path(".git/COMMIT_EDITMSG").open(encoding="utf-8") as f_msg:
        raw_msg = f_msg.read().splitlines()
    subprocess.run(
        [
            "git",
            "commit",
            "--amend",
            "-m",
            raw_msg[0],
            "--no-verify",
        ],
        stderr=subprocess.DEVNULL,
    )


def current_version(file: str) -> str:
    with Path(file).open(encoding="utf-8") as f:
        if search := re.search(BumpVerConf.regex, f.read()):
            return search[0]
    raise NotImplementedError(f"{file} does not implement version value.")


def load_project() -> Dict[str, Any]:
    from .utils import load_pyproject

    return load_pyproject().get("project", {})


def load_config() -> Dict[str, Any]:
    from .utils import load_pyproject

    return load_pyproject().get("tool", {}).get("shelf", {}).get("version", {})


@click.group(name="vs")
def cli_vs():
    """The Versioning commands."""
    pass  # pragma: no cover.


@cli_vs.command()
def conf() -> NoReturn:
    """Return the config data for bumping version."""
    for k, v in load_config().items():
        click.echo(f"{k}: {v!r}")
    sys.exit(0)


@cli_vs.command()
@click.option("-f", "--file", type=click.Path(exists=True))
def changelog(file: Optional[str]) -> NoReturn:
    """Make Changelogs file"""
    if not file:
        file = load_config().get("changelog", None) or "CHANGELOG.md"
    writer_changelog(file)
    sys.exit(0)


@cli_vs.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="The contain version file that able to search with regex.",
)
def current(file: str) -> NoReturn:
    """Return Current Version that read from ``__about__`` by default."""
    if not file:
        file = load_config().get("version", None) or (
            f"./{load_project().get('name', 'unknown')}/__about__.py"
        )
    click.echo(current_version(file))
    sys.exit(0)


@cli_vs.command()
@click.option(
    "-p",
    "--push",
    is_flag=True,
    help="If True, it will push the tag to remote repository",
)
def tag(push: bool) -> NoReturn:
    """Create the Git tag by version from the ``__about__`` file."""
    from .__about__ import __version__

    subprocess.run(["git", "tag", f"v{__version__}"])
    if push:
        subprocess.run(["git", "push", "--tags"])


@cli_vs.command()
@click.argument("action", type=click.STRING, required=1)
@click.option("-f", "--file", type=click.Path(exists=True))
@click.option("-c", "--changelog-file", type=click.Path(exists=True))
@click.option("-v", "--version", type=click.INT, default=1)
@click.option("--ignore-changelog", is_flag=True)
@click.option("--dry-run", is_flag=True)
def bump(
    action: str,
    file: Optional[str],
    changelog_file: Optional[str],
    version: int,
    ignore_changelog: bool,
    dry_run: bool,
) -> NoReturn:
    """Bump Version with specific action."""
    if not file:
        file: str = load_config().get("version", None) or (
            f"./{load_project().get('name', 'unknown')}/__about__.py"
        )
    if not changelog_file:
        changelog_file: str = (
            load_config().get("changelog", None) or "CHANGELOG.md"
        )
    bump2version(
        action,
        file,
        changelog_file,
        ignore_changelog,
        dry_run,
        version,
    )
    sys.exit(0)


if __name__ == "__main__":
    cli_vs.main()
