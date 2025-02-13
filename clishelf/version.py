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
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NoReturn, Optional, TextIO, Union

import click

from .git import CommitLog
from .settings import BumpVerConf
from .utils import Level, load_config, make_color

cli_vs: click.Command

GroupCommitLog = dict[str, list[CommitLog]]
TagGroupCommitLog = dict[str, GroupCommitLog]

UTF8: str = "utf-8"
HEAD: str = "HEAD"
CHANGELOG_HEADER: str = "# Changelogs"
CHANGELOG_LATEST: str = "## Latest Changes"
LINESEP: str = os.linesep


def map_group_commit_logs(
    *,
    all_tags: bool = False,
    is_dt: bool = False,
) -> TagGroupCommitLog:
    """Mapping Group to the getting commit logs function.

    :param all_tags: All tags flag.
    :param is_dt:

    :rtype: GroupCommitLog
    """
    from .git import get_commit_logs

    tag_group_logs: TagGroupCommitLog = defaultdict(lambda: defaultdict(list))
    for log in get_commit_logs(
        all_logs=all_tags,
        excluded=[
            r"pre-commit autoupdate",
            r"^Merge",
        ],
        is_dt=is_dt,
    ):
        tag_group_logs[log.refs][log.msg.mtype].append(log)

    rs: TagGroupCommitLog = {}
    for ref_tag in tag_group_logs:
        rs[ref_tag] = {
            k: sorted(v, key=lambda x: x.date, reverse=True)
            for k, v in tag_group_logs[ref_tag].items()
        }
    return rs


def get_changelog(
    file: Union[str, Path],
    *,
    tags: Optional[list[str]] = None,
    refresh: bool = False,
) -> Iterator[str]:
    """Return the list of content in the changelog file.

    :param file: A change log file path.
    :type file: str
    :param tags:
    :param refresh: A refresh flag

    :rtype: Iterator[str]
    """
    if refresh or not Path(file).exists():
        headers: list[str] = [CHANGELOG_HEADER, CHANGELOG_LATEST]
        if tags:
            headers.extend(f"## {t}" for t in tags)

        # NOTE: Add `""` to all spaces between rows.
        return iter(("|SEP||SEP|".join(headers)).split("|SEP|"))

    with Path(file).open(mode="r", encoding=UTF8) as f_changes:
        changes: list[str] = f_changes.read().splitlines()

    return iter(changes)


def write_group_log(
    writer: TextIO,
    group_logs: GroupCommitLog,
    tag_value: str,
) -> None:
    """Write a group log.

    :param writer:
    :param group_logs:
    :param tag_value:
    """
    from .git import get_commit_prefix_group

    linesep: str = LINESEP
    if not group_logs or any(
        cpt.name in group_logs for cpt in get_commit_prefix_group()
    ):
        linesep: str = f"{LINESEP}{LINESEP}"

    writer.write(f"## {tag_value}{linesep}")

    for group in (
        cpt for cpt in get_commit_prefix_group() if cpt.name in group_logs
    ):
        writer.write(f"### {group.emoji} {group.name}{LINESEP}{LINESEP}")
        for log in group_logs[group.name]:

            subject_fmt: str = (
                load_config()
                .get("version", {})
                .get("commit_subject_format", BumpVerConf.commit_subject_format)
            )
            subject: str = log.msg.subject.format(subject_fmt)

            msg_fmt: str = (
                load_config()
                .get("version", {})
                .get("commit_msg_format", BumpVerConf.commit_msg_format)
            )

            message: str = msg_fmt.format(
                subject=subject,
                datetime=log.date,
            )

            # NOTE: Write commit message to its refs.
            writer.write(f"{message}{LINESEP}")

        writer.write(LINESEP)


def create_changelog(
    file: Union[str, Path],
    *,
    all_tags: bool = False,
    refresh: bool = False,
    is_dt: bool = False,
) -> None:
    """Create Changelog file that generate from Git Log command.

    :param file:
    :param all_tags:
    :param refresh:
    :param is_dt:
    """
    group_logs: TagGroupCommitLog = map_group_commit_logs(
        all_tags=all_tags,
        is_dt=is_dt,
    )
    tags: list[str] = list(filter(lambda t: t != HEAD, group_logs.keys()))
    prev_change: Iterator[str] = get_changelog(file, tags=tags, refresh=refresh)

    with Path(file).open(mode="w", encoding=UTF8, newline="") as writer:
        skip_line: bool = False
        for line in prev_change:
            if line.startswith(CHANGELOG_LATEST):

                # NOTE: Start write group log for the HEAD refs.
                write_group_log(
                    writer,
                    group_logs.get(HEAD, {}),
                    tag_value="Latest Changes",
                )
                skip_line: bool = True

            elif m := re.match(rf"^##\s({BumpVerConf.get_regex(is_dt)})", line):
                get_tag: str = m.group(1)
                if get_tag in tags:  # pragma: no cov
                    write_group_log(
                        writer,
                        group_logs[get_tag],
                        tag_value=get_tag,
                    )
                    skip_line = True
                else:
                    skip_line = False
            elif line.startswith("## "):
                skip_line = False

            if not skip_line:
                writer.write(line + LINESEP)


def write_bump_file(
    param: dict[str, Any],
    *,
    version: int = 1,
    is_dt: bool = False,
) -> None:
    """Writing the ``.bump2version.cfg`` config file at current path.

    :param param:
    :param version:
    :param is_dt:
    """
    files: list[str] = load_config().get("version", {}).get("files", [])
    with Path(".bumpversion.cfg").open(mode="w", encoding=UTF8) as f:
        f.write(
            BumpVerConf.get_version(
                version,
                params=param,
                is_dt=is_dt,
            )
        )

        f.write("\n")
        for file in files:
            f.write(f"\n[bumpversion:file:{file}]\n")


def bump2version(
    action: str,
    file: str,
    changelog_file: str,
    changelog_ignore: bool = False,
    dry_run: bool = False,
    version: int = 1,
    *,
    is_dt: bool = False,
) -> None:  # pragma: no cov
    """Bump version processes that include:

        - write the bump2version file config on the current path
        - write changelog file if not ignore flag
        - commit the above steps to git
        - running bump2version cli for bump the version with the config
        - reset the latest commit
        - remove the bump2version file config
        - commit all change to the latest commit the running from bump2version

    :param action:
    :param file:
    :param changelog_file:
    :param changelog_ignore:
    :param dry_run:
    :param version:
    :param is_dt: A datetime mode flag
    """
    # Start writing ``.bump2version.cfg`` file on current path.
    click.echo("Start write '.bump2version.cfg' config file ...")
    write_bump_file(
        param={
            "changelog": changelog_file,
            "version": current_version(file, is_dt=is_dt),
            "action": action,
            "file": file,
        },
        version=version,
        is_dt=is_dt,
    )

    if not changelog_ignore:
        create_changelog(file=changelog_file)

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

    click.echo("Running the `bump2version` cli with that config file ...")
    try:  # pragma: no cov
        import bumpversion
    except ImportError:
        subprocess.run(
            ["git", "reset", "--hard", "HEAD~1"], stdout=subprocess.DEVNULL
        )
        raise ImportError(
            "The bump function need `bump2version` package. You should install "
            "it by `pip install -U bump2version`"
        ) from None
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
    click.echo("Unlink '.bump2version.cfg' config file ...")
    Path(".bumpversion.cfg").unlink(missing_ok=False)

    with Path(".git/COMMIT_EDITMSG").open(encoding=UTF8) as f_msg:
        raw_msg = f_msg.read().splitlines()

    subprocess.run(["git", "add", "-A"], stderr=subprocess.DEVNULL)
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


def current_version(file: str, *, is_dt: bool = False) -> str:
    """Return the current version.

    :param file:
    :param is_dt:

    :rtype: str
    """
    with Path(file).open(encoding=UTF8) as f:
        if is_dt and (search_dt := re.search(BumpVerConf.regex_dt, f.read())):
            return search_dt[0]
        elif search := re.search(BumpVerConf.regex, f.read()):
            return search[0]
    raise NotImplementedError(f"{file} does not implement version value.")


@click.group(name="vs")
def cli_vs():
    """The Versioning commands."""
    pass  # pragma: no cov


@cli_vs.command()
@click.option("-f", "--file", type=click.Path(exists=True))
@click.option("-n", "--new", is_flag=True)
def changelog(
    file: Optional[str],
    new: bool = False,
) -> NoReturn:  # pragma: no cov
    """Make a changelog file that generate form previous commits."""
    if not file:
        file: str = (
            load_config().get("version", {}).get("changelog", None)
            or "CHANGELOG.md"
        )
    if new:
        create_changelog(file, all_tags=True, refresh=new)
        sys.exit(0)
    create_changelog(file, refresh=new)
    sys.exit(0)


@cli_vs.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="The contain version file that able to search with regex.",
)
def current(file: str) -> NoReturn:  # pragma: no cov
    """Return Current Version that read from ``__about__`` by default."""
    if not file:
        file: str = load_config().get("version", {}).get("version", None) or (
            f"./{load_config().get('project', {}).get('name', 'unknown')}"
            f"/__about__.py"
        )
    click.echo(current_version(file))
    sys.exit(0)


@cli_vs.command()
@click.argument(
    "action",
    type=click.STRING,
    required=1,
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="A about file path that want to write new version.",
)
@click.option(
    "-c",
    "--changelog-file",
    type=click.Path(exists=True),
    help="A changelog file path that want to write new version.",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["normal", "datetime"]),
    help="A bump version mode that should be normal nor datetime.",
    default=None,
)
@click.option(
    "-v",
    "--version",
    type=click.INT,
    default=1,
    help="A version of bump2version config, it default by 1.",
)
@click.option(
    "--ignore-changelog",
    is_flag=True,
    help="If True, it will skip writing changelog step before bump version.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="If True, it will pass --dry-run option to bump2version",
)
def bump(
    action: str,
    file: Optional[str] = None,
    changelog_file: Optional[str] = None,
    mode: Optional[str] = None,
    version: int = 1,
    ignore_changelog: bool = False,
    dry_run: bool = False,
) -> NoReturn:  # pragma: no cov
    """Bump package version with a next tag value with an input action.

    ACTION is the part of action that should be `major`, `minor`, or `patch`.

    \f
    :param action: A action path for bump the next version.
    :type action: str
    :param file:
    :type file: Optional[str] (=None)
    :param changelog_file: Optional[str] (=None)
    :param mode: Optional[str] (=None)
    :param version: int
    :param ignore_changelog: Ignore the changelog file if set be True.
    :type ignore_changelog: boolean
    :param dry_run: Dry run the bumpversion command if set be True.
    :type dry_run: boolean
    """
    vs_conf: dict[str, Any] = load_config().get("version", {})
    if not file:
        file: str = vs_conf.get("version", None) or (
            f"./{load_config().get('project', {}).get('name', 'unknown')}"
            f"/__about__.py"
        )
    if not changelog_file:
        changelog_file: str = vs_conf.get("changelog", None) or "CHANGELOG.md"
    if not mode:
        mode: str = vs_conf.get("mode", "normal")

    assert mode in (
        "datetime",
        "normal",
    ), "`mode` should be normal or datetime only"

    if mode == "normal":
        click.echo(make_color("Be noted that:", Level.INFO))
        click.echo(
            make_color(
                "  * `major`:  means breaking changes and removed deprecations",
                Level.INFO,
            )
        )
        click.echo(
            make_color(
                "  * `minor`:  new features, sometimes automatic migrations",
                Level.INFO,
            )
        )
        click.echo(make_color("  * `patch`:  bug fixes", Level.INFO))

    # NOTE: Start bumping version.
    bump2version(
        action,
        file,
        changelog_file,
        ignore_changelog,
        dry_run,
        version,
        is_dt=(mode == "datetime"),
    )
    sys.exit(0)


if __name__ == "__main__":
    cli_vs.main()
