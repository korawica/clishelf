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
from collections.abc import Generator, Iterator
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import NoReturn, Optional

import click

from .emoji import demojize, get_emojis
from .settings import GitConf
from .utils import (
    Level,
    Profile,
    load_config,
    make_color,
)

cli_git: click.Command
TupleStr = tuple[str, ...]


def get_git_local_config(key: str) -> str | None:
    """Get Git config on the local scope with an input key.

    :rtype: str | None
    """
    try:
        return (
            subprocess.check_output(["git", "config", "--local", key])
            .decode(sys.stdout.encoding)
            .strip()
        )
    except subprocess.CalledProcessError:  # pragma: no cover
        return None


def load_profile() -> Profile:
    """Load profile data from pyproject file or getting from git local config
    and return this values to Profile dataclass.

    :rtype: Profile
    """
    from .utils import load_pyproject

    _authors: dict[str, str] = (
        load_pyproject().get("project", {}).get("authors", {})
    )
    return Profile(
        name=_authors.get("name", get_git_local_config("user.name")),
        email=_authors.get("email", get_git_local_config("user.email")),
    )


@dataclass(frozen=True)
class CommitPrefix:
    name: str
    group: str
    emoji: str

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class CommitPrefixGroup:
    name: str
    emoji: str

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __str__(self) -> str:
        return self.name


def get_commit_prefix() -> tuple[CommitPrefix, ...]:
    """Return tuple of CommitPrefix that setting on the clishelf configuration.

    :rtype: tuple[CommitPrefix, ...]
    """
    conf: list[str] = load_config().get("git", {}).get("commit_prefix", [])
    prefix_conf: TupleStr = tuple(_[0] for _ in conf)
    return tuple(
        CommitPrefix(name=n, group=g, emoji=e)
        for n, g, e in (
            *conf,
            *[p for p in GitConf.commit_prefix if p[0] not in prefix_conf],
        )
    )


def get_commit_prefix_group() -> tuple[CommitPrefixGroup, ...]:
    """Return tuple of CommitPrefixGroup

    :rtype: tuple[CommitPrefixGroup, ...]
    """
    conf: list[str] = (
        load_config().get("git", {}).get("commit_prefix_group", [])
    )
    prefix_conf: TupleStr = tuple(_[0] for _ in conf)
    return tuple(
        CommitPrefixGroup(name=n, emoji=e)
        for n, e in (
            *conf,
            *[
                p
                for p in GitConf.commit_prefix_group
                if p[0] not in prefix_conf
            ],
        )
    )


@lru_cache
def get_git_emojis() -> list[str]:
    cm_prefix: TupleStr = tuple(p.emoji.strip(":") for p in get_commit_prefix())
    return [emojis for emojis in get_emojis() if emojis["alias"] in cm_prefix]


@dataclass
class CommitMsg:
    """Commit Message dataclass that prepare un-emoji-prefix in that message."""

    content: InitVar[str]
    mtype: InitVar[str] = field(default=None)
    body: str = field(default=None)  # NOTE: Mark new-line with ``|``

    def __str__(self) -> str:
        return f"{self.mtype}: {self.content}"

    def __post_init__(self, content: str, mtype: str | None = None) -> None:
        """Post initialize dunder method on this dataclass for preparing
        the content and mtype fields.
        """

        self.content: str = self.__prepare_msg__(
            demojize(content, emojis=get_git_emojis())
        )

        if mtype is None:  # pragma: no cover.
            self.mtype: str = self.__gen_msg_type()

    def __gen_msg_type(self) -> str:
        """Return a message type that getting from the regex."""
        if s := re.search(r"^(?P<emoji>:\w+:)\s(?P<prefix>\w+):", self.content):
            prefix: str = s.groupdict()["prefix"]
            return next(
                (cp.group for cp in get_commit_prefix() if prefix == cp.name),
                "Code Changes",
            )
        return "Code Changes"

    @property
    def mtype_icon(self) -> str:
        return next(
            (
                cpt.emoji
                for cpt in get_commit_prefix_group()
                if cpt.name == self.mtype
            ),
            ":black_nib:",  # ✒️
        )  # pragma: no cover

    @staticmethod
    def __prepare_msg__(content: str) -> str:
        """Prepare string content that receive on post initialize step.

        :param content: A string content that want to prepare.
        :type content: str

        :rtype: str
        :return: A prepared string content that has an emoji prefix.
        """
        if content.startswith("Merge branch "):
            return content.replace(
                "Merge branch ", ":fast_forward: merge: branch "
            )

        if re.match(r"^(:\w+:)\s", content):
            return content

        prefix, content = (
            content.split(":", maxsplit=1)
            if ":" in content
            else ("refactored", content)
        )
        emoji: Optional[str] = None
        for cp in get_commit_prefix():
            if prefix == cp.name:
                emoji = f"{cp.emoji} "
                break
        if emoji is None:
            if (
                load_config()
                .get("git", {})
                .get("commit_prefix_force_fix", False)
            ):
                _prefix: str = demojize(prefix)
                if re.match(r"^(?P<emoji>:\w+:)", _prefix):
                    return f"{_prefix}: {content}"
            raise ValueError(
                f"The prefix of this commit message does not support, "
                f"{prefix!r}."
            )
        return f"{emoji or ''}{prefix}: {content.strip()}"


@dataclass(frozen=True)
class CommitLog:
    """Commit Log dataclass"""

    hash: str
    refs: str
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
                self.refs,
            )
        )


def _validate_commit_msg_warning(lines: list[str]) -> list[str]:
    """Validate Commit message that should to fixed, but it does not impact to
    target repository.

    :param lines: A list of line from commit message.
    :type lines: list[str]

    :rtype: list[str]
    :return: A list of warning message.
    """
    subject: str = lines[0]
    rs: list[str] = []

    # RULE 02: Limit the subject line to 50 characters
    if len(subject) <= 20 or len(subject) > 50:
        rs.append(
            "There should be between 21 and 50 characters in the commit title."
        )
    if len(lines) <= 2:
        rs.append("There should at least 3 lines in your commit message.")

    # RULE 01: Separate subject from body with a blank line
    if lines[1].strip() != "":
        rs.append(
            "There should be an empty line between the commit title and body."
        )

    if not lines[0].strip().endswith("."):
        lines[0] = f"{lines[0].strip()}."
        rs.append("There should not has dot in the end of commit message.")
    return rs


def validate_commit_msg(lines: list[str]) -> tuple[list[str], Level]:
    """Validate Commit message

    :param lines: A list of line from commit message.
    :type lines: List[str]

    :rtype: Tuple[List[str], Level]
    :return: A pair of warning messages and its logging level.
    """
    if not lines:
        return (
            ["Please supply commit message without start with ``#``."],
            Level.ERROR,
        )

    rs: list[str] = _validate_commit_msg_warning(lines)
    for line, msg in enumerate(lines[1:], start=2):
        # RULE 06: Wrap the body at 72 characters
        if len(msg) > 72:
            rs.append(
                f"The commit body should wrap at 72 characters at line: {line}."
            )

    if not rs:
        return (
            ["The commit message has the required pattern."],
            Level.OK,
        )
    return rs, Level.WARNING


def get_latest_tag(default: bool = True) -> str | None:
    """Return the latest tag if it exists, otherwise it will v0.0.0 tag."""
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
        return "v0.0.0" if default else None


def gen_commit_logs(
    tag2head: str,
) -> Generator[list[str], None, None]:  # pragma: no cover.
    """Prepare contents logs to List of commit log."""
    prepare: list[str] = []
    for line in (
        subprocess.check_output(
            [
                "git",
                "log",
                tag2head,
                "--pretty=format:%h|%D|%ad|%an|%ae%n%s%n%b%-C()%n(END)",
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
    tag: str | None = None,
    *,
    all_logs: bool = False,
    excluded: Optional[list[str]] = None,
    is_dt: bool = False,
) -> Iterator[CommitLog]:  # pragma: no cover.
    """Return a list of message that getting from commit log command.

    :param tag: A tag name that want to filter the commit log get to HEAD.
    :type tag: str | None(=None)
    :param all_logs:
    :param excluded:
    :param is_dt: A datetime mode flag.
    :type is_dt: bool(=False)
    """
    from .settings import BumpVerConf

    if tag:
        tag2head: str = f"{tag}..HEAD"
    elif all_logs or not (tag := get_latest_tag(default=False)):
        tag2head = "HEAD"
    else:
        tag2head = f"{tag}..HEAD"
    refs: str = "HEAD"
    for logs in gen_commit_logs(tag2head):
        if any(
            (re.search(s, logs[1]) is not None)
            for s in (excluded or [r"^Merge"])
        ):
            continue
        header: list[str] = logs[0].split("|")
        if ref_tag := [
            ref.strip()
            for ref in header[1].strip().split(",")
            if "tag: " in ref
        ]:
            if search := re.search(
                rf"tag:\sv(?P<version>{BumpVerConf.get_regex(is_dt)})",
                ref_tag[0],
            ):
                refs = search.groupdict()["version"]
        yield CommitLog(
            hash=header[0],
            refs=refs,
            date=datetime.strptime(header[2], "%Y-%m-%d"),
            msg=CommitMsg(
                content=logs[1],
                body="|".join(logs[2:]),
            ),
            author=Profile(
                name=header[3],
                email=header[4],
            ),
        )


def merge2latest_commit(no_verify: bool = False) -> None:  # pragma: no cover.
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit", "-a"]
        + (["--no-verify"] if no_verify else [])
    )


def get_latest_commit(
    file: Optional[str] = None,
    edit: bool = False,
    output_file: bool = False,
) -> list[str]:  # pragma: no cover.
    """Return a list of line that created on commit message file."""
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
    lines: list[str] = [
        msg for msg in raw_msg if not msg.strip().startswith("#")
    ]
    if lines[-1] != "":
        lines += [""]  # Add end-of-file line

    rss, level = validate_commit_msg(lines)
    for rs in rss:
        click.echo(make_color(rs, level))
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
@click.argument(
    "file",
    type=click.STRING,
    default=".git/COMMIT_EDITMSG",
)
@click.option("-e", "--edit", is_flag=True)
@click.option("-o", "--output-file", is_flag=True)
@click.option("-p", "--prepare", is_flag=True)
def cm(
    file: Optional[str],
    edit: bool,
    output_file: bool,
    prepare: bool,
) -> None:  # pragma: no cover.
    """Prepare and show the latest commit message with the commit message
    general rules.

    \f
    :param file:
    :param edit:
    :param output_file:
    :param prepare:
    """
    if not prepare:
        click.echo(
            make_color(
                "\n".join(get_latest_commit(file, edit, output_file)),
                level=Level.OK,
            ),
        )
    else:
        edit: bool = True
        _cm_msg: str = "\n".join(get_latest_commit(file, edit, output_file))
        subprocess.run(
            [
                "git",
                "commit",
                "--amend",
                "-a",
                "--no-verify",
                "-m",
                _cm_msg,
            ],
            stdout=subprocess.DEVNULL,
        )
        click.echo(make_color(_cm_msg, level=Level.OK))
    sys.exit(0)


@cli_git.command()
@click.option("-g", "--group", is_flag=True)
def cm_msg(group: bool = False) -> None:  # pragma: no cover.
    """Return list of commit prefixes"""
    if group:
        for cm_prefix_g in get_commit_prefix_group():
            click.echo(f"{cm_prefix_g.emoji} {cm_prefix_g.name}")
    else:
        for cm_prefix in get_commit_prefix():
            click.echo(
                f"{cm_prefix.emoji} {cm_prefix.name} -> {cm_prefix.group}"
            )
    sys.exit(0)


@cli_git.command()
@click.option("--verify", is_flag=True)
def cm_prev(verify: bool) -> None:  # pragma: no cover.
    """Commit changes to the Previous Commit with same message."""
    merge2latest_commit(no_verify=(not verify))
    sys.exit(0)


@cli_git.command()
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--number", type=click.INT, default=1)
def cm_revert(force: bool, number: int) -> None:  # pragma: no cover.
    """Revert the latest Commit on the Local repository."""
    subprocess.run(["git", "reset", f"HEAD~{number}"])
    if force:
        subprocess.run(["git", "restore", "."])
        subprocess.run(["git", "clean", "-f"])
    sys.exit(0)


@cli_git.command()
@click.argument(
    "branch",
    type=click.STRING,
    default="main",
)
@click.option(
    "-t",
    "--theirs",
    is_flag=True,
    help="If True, it will use `their` strategy if it has conflict",
)
@click.option(
    "-o",
    "--ours",
    is_flag=True,
    help="If True, it will use `ours` strategy if it has conflict",
)
@click.option(
    "-s",
    "--squash",
    is_flag=True,
    help="If True, it will use `squash` merge option.",
)
def mg(
    branch: str,
    theirs: bool = False,
    ours: bool = False,
    squash: bool = False,
) -> None:  # pragma: no cover.
    """Merge change from another branch with strategy, `theirs` or `ours`.

    BRANCH is a name of branch that you want to merge with current branch.

    \f
    :param branch: A name of branch that you want to merge with current branch.
    :param theirs: If True, it will use `their` strategy if it has conflict.
    :param ours: If True, it will use `ours` strategy if it has conflict.
    :param squash: If True, it will use `squash` merge option.
    """
    if theirs and ours:
        raise ValueError("The strategy flag should not True together.")
    elif ours:
        strategy = "ours"
    else:
        strategy = "theirs"
    subprocess.run(
        [
            "git",
            "merge",
            branch,
            "--strategy-option",
            strategy,
            *(["--squash"] if squash else []),
        ],
        stderr=subprocess.DEVNULL,
    )
    sys.exit(0)


@cli_git.command()
def bn_clear() -> NoReturn:  # pragma: no cover.
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
@click.option(
    "-p",
    "--push",
    is_flag=True,
    help="If True, it will auto push to remote",
)
def tg_bump(push: bool = False) -> None:  # pragma: no cover.
    """Create Tag from current version after bumping"""
    latest_tag: str = get_latest_tag(default=False)
    subprocess.run(
        ["git", "tag", "-d", f"{latest_tag}"],
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "fetch", "--prune", "--prune-tags"],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(["git", "tag", f"{latest_tag}"])
    if push:
        subprocess.run(["git", "push", f"{latest_tag}", "--tags"])
    sys.exit(0)


@cli_git.command()
def tg_clear() -> None:  # pragma: no cover.
    """Clear Local Tags that sync from the Remote repository."""
    subprocess.run(
        ["git", "fetch", "--prune", "--prune-tags"],
        stdout=subprocess.DEVNULL,
    )
    sys.exit(0)


if __name__ == "__main__":
    cli_git.main()
