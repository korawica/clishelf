from datetime import datetime
from pathlib import Path
from textwrap import dedent
from unittest.mock import DEFAULT, patch

import clishelf.version as version
from clishelf.git import CommitLog, CommitMsg, Profile


def side_effect_func(*args, **kwargs):
    if ".bumpversion.cfg" in args[0]:
        _ = kwargs
        return Path(__file__).parent / ".bumpversion.cfg"
    elif "__version__.py" in args[0]:
        _ = kwargs
        return Path(__file__).parent / "__version__.py"
    return DEFAULT


@patch("clishelf.git.get_commit_logs")
def test_gen_group_commit_log(mock_get_commit_logs):
    commit_log = CommitLog(
        hash="f477e87",
        refs="HEAD",
        date=datetime(2024, 1, 1),
        msg=CommitMsg(":toolbox: build: add coverage workflow"),
        author=Profile(name="test", email="test@mail.com"),
    )
    mock_get_commit_logs.return_value = iter([commit_log])
    assert version.gen_group_commit_log() == {
        "HEAD": {"Build & Workflow": [commit_log]}
    }


def test_get_changelog():
    changelog_file = Path(__file__).parent / "test_changelog.md"
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
    rs = version.get_changelog(changelog_file)
    assert rs == [
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

    rs = version.get_changelog(changelog_file, refresh=True)
    assert list(rs) == ["# Changelogs", "", "## Latest Changes"]

    rs = version.get_changelog(changelog_file, tags=["0.0.2"], refresh=True)
    assert list(rs) == ["# Changelogs", "", "## Latest Changes", "", "## 0.0.2"]

    changelog_file.unlink()


@patch("clishelf.version.gen_group_commit_log")
def test_writer_changelog(mock_gen_group_commit_log):
    commit_logs = [
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
    mock_gen_group_commit_log.return_value = {
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

    version.writer_changelog(write_changelog_file, all_tags=True)
    assert write_changelog_file.exists()
    assert write_changelog_file.read_text().replace(" ", "") == dedent(
        """# Changelogs

        ## Latest Changes

        ### :black_nib: Code Changes

        - :construction: refactored: add new features (_2024-01-01_)

        ### :package: Build & Workflow

        - :toolbox: build: add coverage workflow (_2024-01-02_)

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
    write_group_log = Path(__file__).parent / "test_write_group_log.md"
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
    with write_group_log.open(mode="w", newline="") as f:
        version.write_group_log(f, group_log, "HEAD")

    assert write_group_log.exists()
    assert write_group_log.read_text().replace(" ", "") == dedent(
        """## HEAD

        ### :package: Build & Workflow

        - :toolbox: build: add coverage workflow (_2024-01-02_)

        """.replace(
            " ", ""
        )
    )
    write_group_log.unlink()

    group_log = {
        "Build & Workflows": [
            CommitLog(
                hash="f477e87",
                refs="HEAD",
                date=datetime(2024, 1, 2),
                msg=CommitMsg(":toolbox: build: add coverage workflow"),
                author=Profile(name="test", email="test@mail.com"),
            )
        ]
    }
    with write_group_log.open(mode="w", newline="") as f:
        version.write_group_log(f, group_log, "HEAD")
    assert write_group_log.exists()
    assert write_group_log.read_text().replace(" ", "") == dedent(
        """## HEAD\n""".replace(" ", "")
    )

    write_group_log.unlink()


@patch("clishelf.version.Path", side_effect=side_effect_func)
def test_write_bump_file(mock_path):
    bump_file = Path(__file__).parent / ".bumpversion.cfg"
    version.write_bump_file(
        param={
            "version": "",
            "changelog": "",
            "file": "__about__.py",
        },
    )
    assert bump_file.exists()

    bump_file.unlink()


@patch("clishelf.version.Path", side_effect=side_effect_func)
def test_current_version(mock_path):
    version_file = Path(__file__).parent / "__version__.py"
    with version_file.open(mode="w") as f:
        f.writelines(["__version__ = 0.0.1\n", "__version_dt__ = 20240101\n"])

    assert version.current_version("__version__.py") == "0.0.1"
    assert version.current_version("__version__.py", is_dt=True) == "20240101"

    version_file.unlink()
