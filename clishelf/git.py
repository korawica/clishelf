from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import InitVar, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click

from .utils import (
    Level,
    make_color,
)

cli_git: click.Command

PROJECT_IDS = ["SLO"]
BRANCH_TYPES = ["feature", "bug", "hot"]

REGEX_PROJECT_IDS = "|".join(PROJECT_IDS)
REGEX_BRANCH_TYPES = "|".join(BRANCH_TYPES)

# Should contain a capturing group to extract the reference:
REGEX_BRANCH: str = (
    rf"^(?:{REGEX_BRANCH_TYPES})/"
    rf"((?:{REGEX_PROJECT_IDS})-[\d]{{1,5}})-[a-z]+(?:-[a-z]+)*$"
)

# Should contain a capturing group to extract the reference
# (note the dot at the end is optional as this script will add it
# automatically for us):
REGEX_MESSAGE = rf"^((?:{REGEX_PROJECT_IDS})-[\d]{{1,5}}): .+\.?$"

# No capturing group. Just checking for the bare minimum:
REGEX_BASIC_MESSAGE = "^.+$"

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

COMMIT_PREFIX = (
    ("feat", "Features", ":dart:"),  # 🎯, 📋 :clipboard:
    ("hotfix", "Fix Bugs", ":fire:"),  # 🔥
    ("fixed", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
    ("fix", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
    ("docs", "Documents", ":page_facing_up:"),  # 📄, 📑 :bookmark_tabs:
    ("style", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
    ("refactored", "Code Changes", ":construction:"),  # 🚧, 💬 :speech_balloon:
    ("refactor", "Code Changes", ":construction:"),  # 🚧, 💬 :speech_balloon:
    ("perf", "Code Changes", ":chart_with_upwards_trend:"),  # 📈, ⌛ :hourglass:
    ("test", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
    ("build", "Build & Workflow", ":toolbox:"),  # 🧰, 📦 :package:
    ("workflow", "Build & Workflow", ":rocket:"),  # 🚀, 🕹️ :joystick:
)

COMMIT_PREFIX_TYPE = (
    ("Features", ":clipboard:"),  # 📋
    ("Code Changes", ":black_nib:"),  # ✒️
    ("Documents", ":bookmark_tabs:"),  # 📑
    ("Fix Bugs", ":hammer_and_wrench:"),  # 🛠️
    ("Build & Workflow", ":package:"),  # 📦
)


@dataclass
class CommitMsg:
    content: InitVar[str]
    mtype: InitVar[str] = None
    body: str = None  # Mark new-line with |

    def __str__(self):
        return f"{self.mtype}: {self.content}"

    def __post_init__(self, content: str, mtype: str):
        self.content: str = self.__prepare_msg(content)
        if not mtype:
            self.mtype: str = self.__gen_msg_type()

    def __gen_msg_type(self) -> str:
        if s := re.search(r"^:\w+:\s(?P<prefix>\w+):", self.content):
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
            ":black_nib:",
        )

    @staticmethod
    def __prepare_msg(content: str) -> str:
        if re.match(r"^:\w+:", content):
            return content

        prefix, content = (
            content.split(":", maxsplit=1)
            if ":" in content
            else ("refactor", content)
        )
        icon: str = ""
        for cp in COMMIT_PREFIX:
            if prefix == cp[0]:
                icon = f"{cp[2]} "
        return f"{icon}{prefix}: {content.strip()}"


@dataclass(frozen=True)
class CommitLog:
    hash: str
    date: date
    msg: CommitMsg
    author: str

    def __str__(self) -> str:
        return "|".join(
            (
                self.hash,
                self.date.strftime("%Y-%m-%d"),
                self.msg.content,
                self.author,
            )
        )


def validate_for_warning(
    lines: List[str],
) -> List[str]:
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
            "There should be an empty line between "
            "the commit title and body."
        )

    if not lines[0].strip().endswith("."):
        lines[0] = f"{lines[0].strip()}."
        results.append("There should not has dot in the end of commit message.")
    return results


def validate_commit_msg(
    lines: List[str],
) -> Tuple[List[str], Level]:
    if not lines:
        return (
            ["Please supply commit message without start with ``#``."],
            Level.ERROR,
        )

    rs = validate_for_warning(lines)
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
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode(sys.stdout.encoding)
        .strip()
    )


def get_latest_tag(default: bool = True) -> Optional[str]:
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


def prepare_commit_logs(tag2head: str):
    """Prepare contents logs to List of commit log."""
    results: List = []
    prepare: List[str] = []
    for line in (
        subprocess.check_output(
            [
                "git",
                "log",
                tag2head,
                "--pretty=format:%h|%ad|%an%n%s%n%b%-C()%n(END)",
                "--date=short",
            ]
        )
        .decode(sys.stdout.encoding)
        .strip()
        .splitlines()
    ):
        if line == "(END)":
            results.append(prepare)
            prepare = []
            continue
        prepare.append(line)
    return results


def get_commit_logs(
    tag: Optional[str] = None,
    all_logs: bool = False,
) -> List[CommitLog]:
    if tag:
        tag2head: str = f"{tag}..HEAD"
    elif all_logs or not (tag := get_latest_tag(default=False)):
        tag2head = "HEAD"
    else:
        tag2head = f"{tag}..HEAD"
    msgs: List[CommitLog] = []
    for _ in prepare_commit_logs(tag2head):
        if "Merge" in _[1]:
            continue

        _s: List[str] = _[0].split("|")
        msgs.append(
            CommitLog(
                hash=_s[0],
                date=datetime.strptime(_s[1], "%Y-%m-%d"),
                msg=CommitMsg(content=_[1], body="|".join(_[2:])),
                author=_s[2],
            )
        )
    return msgs


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
        print(make_color(rs, level))
    if level not in (Level.OK, Level.WARNING):
        sys.exit(1)

    if edit:
        lines[0] = CommitMsg(content=lines[0]).content

    if file and output_file:
        with Path(file).open(mode="w", encoding="utf-8", newline="") as f_msg:
            f_msg.write(f"{os.linesep}".join(lines))
    return lines


def get_branch_ref(branch):
    match = re.findall(REGEX_BRANCH, branch)
    return match[0] if match and match[0] else None


@click.group(name="git")
def cli_git():
    """Extended Git commands"""
    pass


@cli_git.command()
def bn():
    """Show the Current Branch"""
    sys.exit(get_branch_name())


@cli_git.command()
def tl():
    """Show the Latest Tag"""
    sys.exit(get_latest_tag())


@cli_git.command()
@click.option("-t", "--tag", type=click.STRING, default=None)
@click.option("-a", "--all-logs", is_flag=True)
def cl(tag: Optional[str], all_logs: bool):
    """Show the Commit Logs from the latest Tag to HEAD"""
    sys.exit(
        "\n".join(str(x) for x in get_commit_logs(tag=tag, all_logs=all_logs)),
    )


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
        print(
            "\n".join(get_latest_commit(file, edit, output_file)),
        )
        sys.exit(0)
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
            ]
        )


@cli_git.command()
@click.option("--no-verify", is_flag=True)
def commit_previous(no_verify: bool):
    """Commit changes to the Previous Commit with same message"""
    merge2latest_commit(no_verify=no_verify)


@cli_git.command()
@click.option("-f", "--force", is_flag=True)
def commit_revert(force: bool):
    """Revert the latest Commit on this Local"""
    subprocess.run(["git", "reset", "HEAD^"])
    if force:
        subprocess.run(["git", "restore", "."])


@cli_git.command()
def clear_branch():
    """Clear Local Branches that sync from the Remote"""
    subprocess.run(
        ["git", "checkout", "main"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
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


@cli_git.command()
def init_conf():
    """Initialize local GIT config"""
    return 0


if __name__ == "__main__":
    cli_git.main()
