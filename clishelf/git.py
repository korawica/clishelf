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
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Generator, Iterator, List, Optional, Tuple

import click

from .utils import (
    Level,
    Profile,
    make_color,
)

cli_git: click.Command


REGEX_COMMIT_MESSAGE = r"(?P<prefix>\w+)(?:\((?P<topic>\w+)\))?: (?P<header>.+)"

# These branch names are not validated with this same rules
# (permissions should be configured on the server if you want to prevent
# pushing to any of these):
BRANCH_EXCEPTIONS = [
    "feature",
    "dev",
    "main",
    "stable",
    # for quickly fixing critical issues, usually with a temporary solution.
    "hotfix",
    "bugfix",  # for fixing a bug
    "feature",  # for adding, removing or modifying a feature
    "test",  # for experimenting something which is not an issue
    "wip",  # for a work in progress
]

COMMIT_PREFIX: Tuple[Tuple[str, str, str]] = (
    ("feat", "Features", ":dart:"),  # 🎯, 📋 :clipboard:
    ("hotfix", "Fix Bugs", ":fire:"),  # 🔥
    ("fixed", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
    ("fix", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
    ("docs", "Documents", ":page_facing_up:"),  # 📄, 📑 :bookmark_tabs:
    ("styled", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
    ("style", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
    ("refactored", "Code Changes", ":construction:"),  # 🚧, 💬 :speech_balloon:
    ("refactor", "Code Changes", ":construction:"),  # 🚧, 💬 :speech_balloon:
    ("perf", "Code Changes", ":chart_with_upwards_trend:"),  # 📈, ⌛ :hourglass:
    ("tests", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
    ("test", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
    ("build", "Build & Workflow", ":toolbox:"),  # 🧰, 📦 :package:
    ("workflow", "Build & Workflow", ":rocket:"),  # 🚀, 🕹️ :joystick:
)

COMMIT_PREFIX_TYPE: Tuple[Tuple[str, str]] = (
    ("Features", ":clipboard:"),  # 📋
    ("Code Changes", ":black_nib:"),  # ✒️
    ("Documents", ":bookmark_tabs:"),  # 📑
    ("Fix Bugs", ":hammer_and_wrench:"),  # 🛠️
    ("Build & Workflow", ":package:"),  # 📦
)


def load_profile() -> Profile:
    """Load Profile function that return name and email."""
    from .utils import load_pyproject

    _authors: Dict[str, str] = load_pyproject().get("authors", {})
    return Profile(
        name=_authors.get(
            "name",
            (
                subprocess.check_output(
                    ["git", "config", "--local", "user.name"]
                )
                .decode(sys.stdout.encoding)
                .strip()
            ),
        ),
        email=_authors.get(
            "email",
            (
                subprocess.check_output(
                    ["git", "config", "--local", "user.email"]
                )
                .decode(sys.stdout.encoding)
                .strip()
            ),
        ),
    )


@dataclass
class CommitMsg:
    """Commit Message dataclass that prepare un-emoji-prefix in that message."""

    content: InitVar[str]
    mtype: InitVar[str] = field(default=None)
    body: str = field(default=None)  # Mark new-line with |

    def __str__(self):
        return f"{self.mtype}: {self.content}"

    def __post_init__(self, content: str, mtype: str):
        self.content: str = self.__prepare_msg(content)
        if not mtype:
            self.mtype: str = self.__gen_msg_type()

    def __gen_msg_type(self) -> str:
        if s := re.search(r"^(?P<emoji>:\w+:)\s(?P<prefix>\w+):", self.content):
            prefix: str = s.groupdict()["prefix"]
            return next(
                (cp[1] for cp in COMMIT_PREFIX if prefix == cp[0]),
                "Code Changes",
            )
        return "Code Changes"

    @property
    def mtype_icon(self):
        return next(
            (cpt[1] for cpt in COMMIT_PREFIX_TYPE if cpt[0] == self.mtype),
            ":black_nib:",  # ✒️
        )

    @staticmethod
    def __prepare_msg(content: str) -> str:
        if re.match(r"^(?P<emoji>:\w+:)", content):
            return content

        prefix, content = (
            content.split(":", maxsplit=1)
            if ":" in content
            else ("refactored", content)
        )
        icon: str = ""
        for cp in COMMIT_PREFIX:
            if prefix == cp[0]:
                icon = f"{cp[2]} "
        return f"{icon}{prefix}: {content.strip()}"


@dataclass(frozen=True)
class CommitLog:
    """Commit Log dataclass"""

    hash: str
    date: date
    msg: CommitMsg
    author: Profile

    def __str__(self) -> str:
        return "|".join(
            (
                self.hash,
                self.date.strftime("%Y-%m-%d"),
                self.msg.content,
                self.author.name,
                self.author.email,
            )
        )


def validate_for_warning(
    lines: List[str],
) -> List[str]:
    """Validate Commit message that should to fixed, but it does not impact to
    target repository.

    :param lines: A list of line from commit message.
    :type lines: List[str]
    """
    subject: str = lines[0]
    results: List[str] = []

    # RULE 02: Limit the subject line to 50 characters
    if len(subject) <= 20 or len(subject) > 50:
        results.append(
            "There should be between 21 and 50 characters in the commit title."
        )
    if len(lines) <= 2:
        results.append("There should at least 3 lines in your commit message.")

    # RULE 01: Separate subject from body with a blank line
    if lines[1].strip() != "":
        results.append(
            "There should be an empty line between the commit title and body."
        )

    if not lines[0].strip().endswith("."):
        lines[0] = f"{lines[0].strip()}."
        results.append("There should not has dot in the end of commit message.")
    return results


def validate_commit_msg(
    lines: List[str],
) -> Tuple[List[str], Level]:
    """"""
    if not lines:
        return (
            ["Please supply commit message without start with ``#``."],
            Level.ERROR,
        )

    rs: List[str] = validate_for_warning(lines)
    if rs:
        return rs, Level.WARNING

    has_story_id: bool = False
    for line in lines[1:]:
        # RULE 06: Wrap the body at 72 characters
        if len(line) > 72:
            rs.append("The commit body should wrap at 72 characters.")

        if line.startswith("["):
            has_story_id = True

    if not has_story_id:
        rs.append("Please add a Story ID in the commit message.")

    if not rs:
        return (
            ["The commit message has the required pattern."],
            Level.OK,
        )
    return rs, Level.WARNING


def get_branch_name() -> str:
    """Return current branch name."""
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode(sys.stdout.encoding)
        .strip()
    )


def get_latest_tag(default: bool = True) -> Optional[str]:
    """Return the latest tag if it exists, otherwise it will return the
    version from ``.__about__`` file.
    """
    try:
        return (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL,
            )
            .decode(sys.stdout.encoding)
            .strip()
        )
    except subprocess.CalledProcessError:
        if default:
            from .__about__ import __version__

            return f"v{__version__}"
        return None


def prepare_commit_logs(tag2head: str) -> Generator[List[str], None, None]:
    """Prepare contents logs to List of commit log."""
    prepare: List[str] = []
    for line in (
        subprocess.check_output(
            [
                "git",
                "log",
                tag2head,
                "--pretty=format:%h|%ad|%an|%ae%n%s%n%b%-C()%n(END)",
                "--date=short",
            ]
        )
        .decode(sys.stdout.encoding)
        .strip()
        .splitlines()
    ):
        if line == "(END)":
            yield prepare
            prepare = []
            continue
        prepare.append(line)


def get_commit_logs(
    tag: Optional[str] = None,
    *,
    all_logs: bool = False,
    excluded: Optional[List[str]] = None,
) -> Iterator[CommitLog]:
    """Return a list of commit message logs."""
    _exc: List[str] = excluded or [r"^Merge"]
    if tag:
        tag2head: str = f"{tag}..HEAD"
    elif all_logs or not (tag := get_latest_tag(default=False)):
        tag2head = "HEAD"
    else:
        tag2head = f"{tag}..HEAD"
    for _ in prepare_commit_logs(tag2head):
        if any((re.search(s, _[1]) is not None) for s in _exc):
            continue
        header: List[str] = _[0].split("|")
        yield CommitLog(
            hash=header[0],
            date=datetime.strptime(header[1], "%Y-%m-%d"),
            msg=CommitMsg(
                content=_[1],
                body="|".join(_[2:]),
            ),
            author=Profile(
                name=header[2],
                email=header[3],
            ),
        )


def merge2latest_commit(no_verify: bool = False):
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit", "-a"]
        + (["--no-verify"] if no_verify else [])
    )


def get_latest_commit(
    file: Optional[str] = None,
    edit: bool = False,
    output_file: bool = False,
) -> List[str]:
    if file:
        with Path(file).open(encoding="utf-8") as f_msg:
            raw_msg = f_msg.read().splitlines()
    else:
        raw_msg = (
            subprocess.check_output(
                ["git", "log", "HEAD^..HEAD", "--pretty=format:%B"]
            )
            .decode(sys.stdout.encoding)
            .strip()
            .splitlines()
        )
    lines: List[str] = [
        msg for msg in raw_msg if not msg.strip().startswith("#")
    ]
    if lines[-1] != "":
        lines += [""]  # Add end-of-file line

    rss, level = validate_commit_msg(lines)
    for rs in rss:
        click.echo(make_color(rs, level), file=sys.stdout)
    if level not in (Level.OK, Level.WARNING):
        sys.exit(1)

    if edit:
        lines[0] = CommitMsg(content=lines[0]).content

    if file and output_file:
        with Path(file).open(mode="w", encoding="utf-8", newline="") as f_msg:
            f_msg.write(f"{os.linesep}".join(lines))
    return lines


@click.group(name="git")
def cli_git():
    """The Extended Git commands"""
    pass  # pragma: no cover.


@cli_git.command()
def bn():
    """Show the Current Branch name."""
    click.echo(get_branch_name(), file=sys.stdout)
    sys.exit(0)


@cli_git.command()
def tg():
    """Show the Latest Tag if it exists, otherwise it will show version from
    about file.
    """
    click.echo(get_latest_tag(), file=sys.stdout)
    sys.exit(0)


@cli_git.command()
@click.option("-t", "--tag", type=click.STRING, default=None)
@click.option("-a", "--all-logs", is_flag=True)
def cm_log(tag: Optional[str], all_logs: bool):
    """Show the Commit Logs from the latest Tag to HEAD."""
    click.echo(
        "\n".join(str(x) for x in get_commit_logs(tag=tag, all_logs=all_logs)),
        file=sys.stdout,
    )
    sys.exit(0)


@cli_git.command()
@click.option("-f", "--file", type=click.STRING, default=None)
@click.option("-l", "--latest", is_flag=True)
@click.option("-e", "--edit", is_flag=True)
@click.option("-o", "--output-file", is_flag=True)
@click.option("-p", "--prepare", is_flag=True)
def cm(
    file: Optional[str],
    latest: bool,
    edit: bool,
    output_file: bool,
    prepare: bool,
):
    """Show the latest Commit message"""
    if latest and not file:
        file = ".git/COMMIT_EDITMSG"
    if not prepare:
        click.echo(
            make_color(
                "\n".join(get_latest_commit(file, edit, output_file)),
                level=Level.OK,
            ),
        )
    else:
        edit: bool = True
        cm_msg: str = "\n".join(get_latest_commit(file, edit, output_file))
        subprocess.run(
            [
                "git",
                "commit",
                "--amend",
                "-a",
                "--no-verify",
                "-m",
                cm_msg,
            ],
            stdout=subprocess.DEVNULL,
        )
        click.echo(make_color(cm_msg, level=Level.OK))
    sys.exit(0)


@cli_git.command()
@click.option("--no-verify", is_flag=True)
def cm_previous(no_verify: bool):
    """Commit changes to the Previous Commit with same message."""
    merge2latest_commit(no_verify=no_verify)
    sys.exit(0)


@cli_git.command()
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--number", type=click.INT, default=1)
def cm_revert(force: bool, number: int):
    """Revert the latest Commit on the Local repository."""
    subprocess.run(["git", "reset", f"HEAD~{number}"])
    if force:
        subprocess.run(["git", "restore", "."])
    sys.exit(0)


@cli_git.command()
def bn_clear():
    """Clear Local Branches that sync from the Remote repository."""
    subprocess.run(
        ["git", "checkout", "main"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        # Or, use ``git remote prune origin``.
        ["git", "remote", "update", "origin", "--prune"],
        stdout=subprocess.DEVNULL,
    )
    branches = (
        subprocess.check_output(["git", "branch", "-vv"])
        .decode(sys.stdout.encoding)
        .strip()
        .splitlines()
    )
    for branch in branches:
        if ": gone]" in branch:
            subprocess.run(["git", "branch", "-D", branch.strip().split()[0]])
    subprocess.run(["git", "checkout", "-"])
    sys.exit(0)


@cli_git.command()
def tg_clear():
    """Clear Local Tags that sync from the Remote repository."""
    subprocess.run(
        ["git", "fetch", "--prune", "--prune-tags"],
        stdout=subprocess.DEVNULL,
    )
    sys.exit(0)


@cli_git.command()
@click.option(
    "--store",
    is_flag=True,
    help="(=False) Store credential flag.",
)
@click.option(
    "--prune-tag",
    is_flag=True,
    help="(=False) Set Fetch handle prune tag.",
)
def init_conf(store: bool, prune_tag: bool):
    """Initialize GIT config on local"""
    pf: Profile = load_profile()
    subprocess.run(
        ["git", "config", "--local", "user.name", f'"{pf.name}"'],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "config", "--local", "user.email", f'"{pf.email}"'],
        stdout=subprocess.DEVNULL,
    )
    st = "store" if store else '""'
    subprocess.run(
        ["git", "config", "--local", "credential.helper", st],
        stdout=subprocess.DEVNULL,
    )
    if prune_tag:
        # If you only want to prune tags when fetching from a specific remote.
        # ["git", "config", "remote.origin.pruneTags", "true"]
        subprocess.run(
            # Or, able to use ``git fetch -p -P``.
            ["git", "config", "--local", "fetch.pruneTags", "true"],
            stdout=subprocess.DEVNULL,
        )
    sys.exit(0)


@cli_git.command()
def profile():
    """Show Profile object that contain Name and Email of Author"""
    click.echo(load_profile(), file=sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    cli_git.main()
