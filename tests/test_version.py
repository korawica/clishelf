# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from unittest.mock import DEFAULT, patch

from clishelf.git import CommitLog, CommitMsg, Profile
from clishelf.version import (
    create_changelog,
    current_version,
    get_changelog,
    map_group_commit_logs,
    write_bump_file,
    write_group_log,
)


def side_effect_func(*args, **kwargs):
    _ = kwargs
    if ".bumpversion.cfg" in args[0]:
        return Path(__file__).parent / ".bumpversion.cfg"
    elif "__version__.py" in args[0]:
        return Path(__file__).parent / "__version__.py"
    return DEFAULT


@patch("clishelf.git.get_commit_logs")
def test_map_group_commit_logs(mock_get_commit_logs):
    commit_log = CommitLog(
        hash="f477e87",
        refs="HEAD",
        date=datetime(2024, 1, 1),
        msg=CommitMsg(":toolbox: build: add coverage workflow"),
        author=Profile(name="test", email="test@mail.com"),
    )
    mock_get_commit_logs.return_value = iter([commit_log])

    assert map_group_commit_logs() == {
        "HEAD": {"Build & Workflow": [commit_log]}
    }


def test_get_changelog(test_path: Path):
    changelog_file: Path = test_path / "test_changelog.md"
    with changelog_file.open(mode="w") as f:
        f.writelines(
            [
                "# Changelogs\n\n",
                "## Latest Changes\n\n",
                "## 0.0.2\n\n",
                "### Features\n\n",
                "- :dart: feat: second commit (_2024-01-02_)\n\n",
                "## 0.0.1\n\n",
                "### Features\n\n",
                "- :dart: feat: first initial (_2024-01-01_)\n",
            ]
        )
    rs: Iterator[str] = get_changelog(changelog_file)
    assert list(rs) == [
        "# Changelogs",
        "",
        "## Latest Changes",
        "",
        "## 0.0.2",
        "",
        "### Features",
        "",
        "- :dart: feat: second commit (_2024-01-02_)",
        "",
        "## 0.0.1",
        "",
        "### Features",
        "",
        "- :dart: feat: first initial (_2024-01-01_)",
    ]

    rs = get_changelog(changelog_file, refresh=True)
    assert list(rs) == ["# Changelogs", "", "## Latest Changes"]

    rs = get_changelog(changelog_file, tags=["0.0.2"], refresh=True)
    assert list(rs) == ["# Changelogs", "", "## Latest Changes", "", "## 0.0.2"]

    changelog_file.unlink()


@patch("clishelf.version.map_group_commit_logs")
def test_create_changelog(mock_map_group_commit_logs):
    commit_logs: list[CommitLog] = [
        CommitLog(
            hash="f477e87",
            refs="HEAD",
            date=datetime(2024, 1, 2),
            msg=CommitMsg(":toolbox: build: add coverage workflow"),
            author=Profile(name="test", email="test@mail.com"),
        ),
        CommitLog(
            hash="dc25a22",
            refs="HEAD",
            date=datetime(2024, 1, 1),
            msg=CommitMsg(":construction: refactored: add new features"),
            author=Profile(name="test", email="test@mail.com"),
        ),
    ]
    mock_map_group_commit_logs.return_value = {
        "HEAD": {
            "Build & Workflow": [commit_logs[0]],
            "Code Changes": [commit_logs[1]],
        },
    }
    write_changelog_file = Path(__file__).parent / "test_write_changelog.md"
    with write_changelog_file.open(mode="w") as f:
        f.writelines(
            [
                "# Changelogs\n\n",
                "## Latest Changes\n\n",
                "## 0.0.1\n\n",
                "### Features\n\n",
                "- :dart: feat: first initial (_2024-01-01_)\n\n",
                "## NOTED\n\n",
                "This line should comment for EOF\n\n",
            ]
        )

    create_changelog(write_changelog_file, all_tags=True)

    assert write_changelog_file.exists()
    assert write_changelog_file.read_text().replace(" ", "") == dedent(
        """# Changelogs

        ## Latest Changes

        ### :black_nib: Code Changes

        - :construction: refactored: add new features

        ### :package: Build & Workflow

        - :toolbox: build: add coverage workflow

        ## 0.0.1

        ### Features

        - :dart: feat: first initial (_2024-01-01_)

        ## NOTED

        This line should comment for EOF

        """.replace(
            " ", ""
        )
    )
    write_changelog_file.unlink()


def test_write_group_log():
    test_file_path: Path = Path(__file__).parent / "test_write_group_log.md"
    group_log = {
        "Build & Workflow": [
            CommitLog(
                hash="f477e87",
                refs="HEAD",
                date=datetime(2024, 1, 2),
                msg=CommitMsg(":toolbox: build: add coverage workflow"),
                author=Profile(name="test", email="test@mail.com"),
            )
        ]
    }
    with test_file_path.open(mode="w", newline="") as f:
        write_group_log(f, group_log, "HEAD")

    assert test_file_path.exists()
    assert test_file_path.read_text().replace(" ", "") == dedent(
        """## HEAD

        ### :package: Build & Workflow

        - :toolbox: build: add coverage workflow

        """.replace(
            " ", ""
        )
    )

    test_file_path.unlink()

    group_log = {
        "Build & Workflow Not Exist": [
            CommitLog(
                hash="f477e87",
                refs="HEAD",
                date=datetime(2024, 1, 2),
                msg=CommitMsg(":toolbox: build: add coverage workflow"),
                author=Profile(name="test", email="test@mail.com"),
            )
        ]
    }
    with test_file_path.open(mode="w", newline="") as f:
        write_group_log(f, group_log, "HEAD")

    assert test_file_path.exists()
    assert test_file_path.read_text().replace(" ", "") == dedent(
        """## HEAD\n""".replace(" ", "")
    )

    test_file_path.unlink()


@patch("clishelf.utils.load_pyproject")
def test_write_group_log_with_change_format(mock_load_pyproject):
    mock_load_pyproject.return_value = {
        "tool": {
            "shelf": {
                "version": {
                    "commit_subject_format": "{emoji} {subject}",
                    "commit_msg_format": "- {subject} (_{datetime:%Y%m%d}_)",
                },
            },
        },
    }
    test_file_path: Path = (
        Path(__file__).parent / "test_write_group_log_with_fmt.md"
    )
    group_log = {
        "Build & Workflow": [
            CommitLog(
                hash="f477e87",
                refs="HEAD",
                date=datetime(2024, 1, 2),
                msg=CommitMsg(":toolbox: build: add coverage workflow"),
                author=Profile(name="test", email="test@mail.com"),
            )
        ]
    }
    with test_file_path.open(mode="w", newline="") as f:
        write_group_log(f, group_log, "HEAD")

    assert test_file_path.exists()
    assert test_file_path.read_text().replace(" ", "") == dedent(
        """## HEAD

        ### :package: Build & Workflow

        - :toolbox: add coverage workflow (_20240102_)

        """.replace(
            " ", ""
        )
    )

    test_file_path.unlink()


@patch("clishelf.version.Path", side_effect=side_effect_func)
def test_write_bump_file(mock_path):
    bump_file_path: Path = Path(__file__).parent / ".bumpversion.cfg"

    write_bump_file(
        param={
            "version": "",
            "changelog": "",
            "file": "__about__.py",
        },
    )

    assert bump_file_path.exists()

    bump_file_path.unlink()


@patch("clishelf.version.Path", side_effect=side_effect_func)
def test_current_version(mock_path):
    version_file_path: Path = Path(__file__).parent / "__version__.py"

    with version_file_path.open(mode="w") as f:
        f.writelines(["__version__ = 0.0.1\n", "__version_dt__ = 20240101\n"])

    assert current_version("__version__.py") == "0.0.1"
    assert current_version("__version__.py", is_dt=True) == "20240101"

    version_file_path.unlink()
