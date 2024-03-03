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
from functools import lru_cache
from pathlib import Path
from typing import Dict, Generator, Iterator, List, NoReturn, Optional, Tuple

import click

from .emoji import get_emojis
from .settings import GitConf
from .utils import (
    Level,
    Profile,
    load_config,
    make_color,
)

cli_git: click.Command


def load_profile() -> Profile:
    """Load Profile function that return name and email."""
    from .utils import load_pyproject

    _authors: Dict[str, str] = (
        load_pyproject().get("project", {}).get("authors", {})
    )
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

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return self.name


def get_commit_prefix() -> Tuple[CommitPrefix, ...]:
    """Return tuple of CommitPrefix"""
    conf: List[str] = load_config().get("git", {}).get("commit_prefix", [])
    prefix_conf: Tuple[str, ...] = tuple(_[0] for _ in conf)
    return tuple(
        CommitPrefix(name=n, group=g, emoji=e)
        for n, g, e in (
            *conf,
            *[p for p in GitConf.commit_prefix if p[0] not in prefix_conf],
        )
    )


def get_commit_prefix_group() -> Tuple[CommitPrefixGroup, ...]:
    """Return tuple of CommitPrefixGroup"""
    conf: List[str] = (
        load_config().get("git", {}).get("commit_prefix_group", [])
    )
    prefix_conf: Tuple[str, ...] = tuple(_[0] for _ in conf)
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
def get_git_emojis():
    cm_prefix = tuple(p.emoji.strip(":") for p in get_commit_prefix())
    return [emojis for emojis in get_emojis() if emojis["alias"] in cm_prefix]


def git_demojize(msg: str):
    for emojis in get_git_emojis():
        if (emoji := emojis["emoji"]) in msg:
            msg = msg.replace(emoji, f':{emojis["alias"]}:')
    return msg


@dataclass
class CommitMsg:
    """Commit Message dataclass that prepare un-emoji-prefix in that message."""

    content: InitVar[str]
    mtype: InitVar[str] = field(default=None)
    body: str = field(default=None)  # Mark new-line with |

    def __str__(self):
        return f"{self.mtype}: {self.content}"

    def __post_init__(self, content: str, mtype: Optional[str] = None) -> None:
        self.content: str = self.__prepare_msg(git_demojize(content))
        if mtype is None:  # pragma: no cover.
            self.mtype: str = self.__gen_msg_type()

    def __gen_msg_type(self) -> str:
        if s := re.search(r"^(?P<emoji>:\w+:)\s(?P<prefix>\w+):", self.content):
            prefix: str = s.groupdict()["prefix"]
            return next(
                (cp.group for cp in get_commit_prefix() if prefix == cp.name),
                "Code Changes",
            )
        return "Code Changes"

    @property
    def mtype_icon(self):
        return next(
            (
                cpt.emoji
                for cpt in get_commit_prefix_group()
                if cpt.name == self.mtype
            ),
            ":black_nib:",  # ✒️
        )  # pragma: no cover

    @staticmethod
    def __prepare_msg(content: str) -> str:
        if re.match(r"^(?P<emoji>:\w+:)", content):
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
        if emoji is None:
            raise ValueError(
                f"The prefix of this commit message does not support, "
                f"{prefix!r}."
            )
        return f"{emoji}{prefix}: {content.strip()}"


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


def _validate_for_warning(
    lines: List[str],
) -> List[str]:
    """Validate Commit message that should to fixed, but it does not impact to
    target repository.

    :param lines: A list of line from commit message.
    :type lines: List[str]

    :rtype: List[str]
    :return: A list of warning message.
    """
    subject: str = lines[0]
    rs: List[str] = []

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


def validate_commit_msg(
    lines: List[str],
) -> Tuple[List[str], Level]:
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

    rs: List[str] = _validate_for_warning(lines)
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


def get_branch_name() -> str:
    """Return current branch name."""
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode(sys.stdout.encoding)
        .strip()
    )


def get_latest_tag(default: bool = True) -> str:
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
    except subprocess.CalledProcessError as err:
        if default:
            from .__about__ import __version__

            return f"v{__version__}"
        raise RuntimeError(
            "Can not extract the latest version from this project"
        ) from err


def gen_commit_logs(
    tag2head: str,
) -> Generator[List[str], None, None]:  # pragma: no cover.
    """Prepare contents logs to List of commit log."""
    prepare: List[str] = []
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
    tag: Optional[str] = None,
    *,
    all_logs: bool = False,
    excluded: Optional[List[str]] = None,
    is_dt: bool = False,
) -> Iterator[CommitLog]:  # pragma: no cover.
    """Return a list of commit message logs."""
    from .settings import BumpVerConf

    regex: str = BumpVerConf.get_regex(is_dt)
    _exc: List[str] = excluded or [r"^Merge"]
    if tag:
        tag2head: str = f"{tag}..HEAD"
    elif all_logs or not (tag := get_latest_tag(default=False)):
        tag2head = "HEAD"
    else:
        tag2head = f"{tag}..HEAD"
    refs: str = "HEAD"
    for logs in gen_commit_logs(tag2head):
        if any((re.search(s, logs[1]) is not None) for s in _exc):
            continue
        header: List[str] = logs[0].split("|")
        if ref_tag := [
            ref.strip()
            for ref in header[1].strip().split(",")
            if "tag: " in ref
        ]:
            if search := re.search(rf"tag:\sv(?P<version>{regex})", ref_tag[0]):
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


def merge2latest_commit(no_verify: bool = False):  # pragma: no cover.
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit", "-a"]
        + (["--no-verify"] if no_verify else [])
    )


def get_latest_commit(
    file: Optional[str] = None,
    edit: bool = False,
    output_file: bool = False,
) -> List[str]:  # pragma: no cover.
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
@click.option("-d", "--datetime-mode", is_flag=True)
def log(
    tag: Optional[str],
    all_logs: bool,
    datetime_mode: bool,
):  # pragma: no cover.
    """Show the Commit Logs from the latest Tag to HEAD."""
    click.echo(
        "\n".join(
            str(x)
            for x in get_commit_logs(
                tag=tag,
                all_logs=all_logs,
                is_dt=datetime_mode,
            )
        ),
        file=sys.stdout,
    )
    sys.exit(0)


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
):  # pragma: no cover.
    """Show the latest Commit message"""
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
def cm_msg(group: bool = False) -> NoReturn:  # pragma: no cover.
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
def cm_prev(verify: bool) -> NoReturn:  # pragma: no cover.
    """Commit changes to the Previous Commit with same message."""
    merge2latest_commit(no_verify=(not verify))
    sys.exit(0)


@cli_git.command()
@click.option("-f", "--force", is_flag=True)
@click.option("-n", "--number", type=click.INT, default=1)
def cm_revert(force: bool, number: int):  # pragma: no cover.
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
) -> NoReturn:  # pragma: no cover.
    """Merge change from another branch with strategy, `theirs` or `ours`.

    BRANCH is a name of branch that you want to merge with current branch.

    \f
    :param branch:
    :param theirs:
    :param ours:
    :param squash:
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
def tg_bump(push: bool = False) -> NoReturn:  # pragma: no cover.
    """Create Tag from current version after bumping"""
    latest_tag: str = get_latest_tag(default=False)
    subprocess.run(
        ["git", "tag", "-d", f"v{latest_tag}"],
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "fetch", "--prune", "--prune-tags"],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(["git", "tag", f"v{latest_tag}"])
    if push:
        subprocess.run(["git", "push", f"v{latest_tag}", "--tags"])
    sys.exit(0)


@cli_git.command()
def tg_clear() -> NoReturn:  # pragma: no cover.
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
    help="If True, it will set store credential.",
)
@click.option(
    "--prune-tag",
    is_flag=True,
    help="If True, it will set fetch handle prune tag.",
)
def init(store: bool, prune_tag: bool) -> NoReturn:  # pragma: no cover.
    """Initialize GIT config on local"""
    if not Path(".git").exists():
        click.echo("Start initialize git on current path ...")
        subprocess.run(["git", "init"], stdout=subprocess.DEVNULL)
    profile: Profile = load_profile()
    subprocess.run(
        ["git", "config", "--local", "user.name", f'"{profile.name}"'],
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "config", "--local", "user.email", f'"{profile.email}"'],
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
def pf() -> NoReturn:  # pragma: no cover.
    """Show Profile object that contain Name and Email of Author"""
    click.echo(load_profile(), file=sys.stdout)
    sys.exit(0)


@cli_git.command()
def df() -> NoReturn:  # pragma: no cover.
    """Show changed files from previous commit to HEAD"""
    # NOTE: We can use `git show --name-only HEAD~1`, but it got commit message.
    subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"])
    sys.exit(0)


if __name__ == "__main__":
    cli_git.main()
