import datetime
import sys
from unittest.mock import DEFAULT, patch

import pytest

import clishelf.git as git
from clishelf.emoji import demojize


def side_effect_func(*args, **kwargs):
    if any(["git", "config", "--local", "user.name"] == a for a in args):
        _ = kwargs
        return "Test User".encode(encoding=sys.stdout.encoding)
    elif any(["git", "config", "--local", "user.email"] == a for a in args):
        _ = kwargs
        return "test@mail.com".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


def side_effect_bn_tg_func(*args, **kwargs):
    if any(["git", "rev-parse", "--abbrev-ref", "HEAD"] == a for a in args):
        _ = kwargs
        return "0.1.2".encode(encoding=sys.stdout.encoding)
    elif any(["git", "describe", "--tags", "--abbrev=0"] == a for a in args):
        _ = kwargs
        return "v0.0.1".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


def test_commit_prefix_model():
    rs = git.CommitPrefix(
        name="test",
        group="A",
        emoji=":dart:",
    )
    assert hash(rs) == hash(rs.name)
    assert "test" == str(rs)


def test_commit_prefix_group_model():
    rs = git.CommitPrefixGroup(
        name="test",
        emoji=":dart:",
    )
    assert hash(rs) == hash(rs.name)
    assert "test" == str(rs)


def test_commit_message_model(make_yaml_conf):
    msg = git.CommitMsg(
        content=":dart: feat: start initial testing",
        mtype=None,
    )
    assert "Features: :dart: feat: start initial testing" == str(msg)

    msg = git.CommitMsg(
        content=":dart: demo: start initial testing",
        mtype=None,
    )
    assert "Code Changes: :dart: demo: start initial testing" == str(msg)

    msg = git.CommitMsg(
        content=":dart: start initial testing",
        mtype=None,
    )
    assert "Code Changes: :dart: refactored: start initial testing" == str(msg)

    msg = git.CommitMsg(
        content="⬆️ deps: upgrade dependencies from main branch (#63)",
        mtype=None,
    )
    assert (
        "Dependencies: :arrow_up: deps: upgrade dependencies from "
        "main branch (#63)"
    ) == str(msg)

    msg = git.CommitMsg(
        content="Merge branch 'main' into dev",
        mtype=None,
    )
    assert "Code Changes: :fast_forward: merge: branch 'main' into dev" == str(
        msg
    )

    msg = git.CommitMsg(content="commit message that not pass prefix")
    assert (
        "Code Changes: :construction: refactored: commit message that not "
        "pass prefix"
    ) == str(msg)

    msg = git.CommitMsg(
        content="commit message that not pass prefix", mtype="Dependencies"
    )
    assert (
        "Dependencies: :construction: refactored: commit message that not "
        "pass prefix"
    ) == str(msg)

    msg = git.CommitMsg(
        content="not_exists: commit message that not pass prefix"
    )
    assert (
        "Code Changes: :construction: not_exists: commit message that not "
        "pass prefix"
    ) == str(msg)

    msg = git.CommitMsg(
        content="merge: branch 'main' of https://github.com/korawica"
    )
    assert (
        "Code Changes: :fast_forward: merge: branch 'main' of "
        "https://github.com/korawica"
    ) == str(msg)


@patch("clishelf.utils.load_pyproject")
def test_commit_message_model_change_format(mock_load_pyproject):
    mock_load_pyproject.return_value = {
        "tool": {
            "shelf": {"git": {"commit_msg_format": "{prefix}: {subject}"}},
        },
    }
    msg = git.CommitMsg(content=":dart: demo: start initial testing")
    assert "Code Changes: demo: start initial testing" == str(msg)


@patch("clishelf.utils.load_pyproject")
def test_commit_message_model_raise(mock_load_pyproject):
    mock_load_pyproject.return_value = {
        "tool": {
            "shelf": {
                "git": {
                    "commit_prefix_force_fix": False,
                    "commit_prefix_pre_demojize": False,
                },
            },
        },
    }

    with pytest.raises(ValueError):
        git.CommitMsg(
            content="⬆️ demo: start initial testing",
            mtype=None,
        )

    with pytest.raises(ValueError):
        git.CommitMsg(
            content="demo: start initial testing",
            mtype=None,
        )

    with pytest.raises(ValueError):
        git.CommitMsg(content="not_exists: some content")


def test_commit_log_model():
    log = git.CommitLog(
        hash="test",
        refs="HEAD",
        date=datetime.date(2023, 1, 1),
        msg=git.CommitMsg(":dart: feat: start initial testing"),
        author=git.Profile(
            name="test",
            email="test@mail.com",
        ),
    )
    assert (
        "test|2023-01-01|:dart: feat: start initial testing|"
        "test|test@mail.com|HEAD"
    ) == str(log)


@patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
@patch("clishelf.utils.load_pyproject")
def test_load_profile(mock_load_pyproject, mock):
    mock_load_pyproject.return_value = {}
    rs = git.load_profile()

    assert mock.called
    assert isinstance(rs, git.Profile)
    assert "Test User" == rs.name
    assert "test@mail.com" == rs.email


def test_get_commit_prefix():
    assert 34 == len(list(git.get_commit_prefix()))


def test_get_commit_prefix_group():
    data: tuple[git.CommitPrefixGroup, ...] = git.get_commit_prefix_group()
    feat: git.CommitPrefixGroup = [cm for cm in data if cm.name == "Features"][
        0
    ]
    assert ":tada:" == feat.emoji

    # NOTE: The first group should be the 0 priority
    assert data[0].priority == 0

    # NOTE: The last group should be the 0 priority
    assert data[-1].priority == 90


@patch(
    "clishelf.git.subprocess.check_output",
    side_effect=side_effect_bn_tg_func,
)
def test_get_latest_tag(mock):
    result = git.get_latest_tag()

    assert mock.called
    assert "v0.0.1" == result


def test_git_demojize():
    assert "test :fire: :fire:" == demojize(
        "test 🔥 :fire:", emojis=git.get_git_emojis()
    )


def test_validate_commit_msg_warning():
    rs = git._validate_commit_msg_warning([":dart: feat: demo", ""])
    assert rs == [
        (
            "There should be between 21 and 50 characters in the "
            "commit title."
        ),
        "There should at least 3 lines in your commit message.",
        "There should not has dot in the end of commit message.",
    ]

    rs = git._validate_commit_msg_warning(
        [":dart: feat: demo test validate for warning.", "empty"]
    )
    assert rs == [
        "There should at least 3 lines in your commit message.",
        "There should be an empty line between the commit title " "and body.",
    ]

    rs = git._validate_commit_msg_warning(
        [
            ":dart: feat: demo test validate for warning.",
            "",
            "body of commit log",
            "",
        ]
    )
    assert rs == []


def test_validate_commit_msg():
    rs = git.validate_commit_msg([])
    assert rs == (
        ["Please supply commit message without start with ``#``."],
        git.Level.ERROR,
    )

    rs = git.validate_commit_msg(
        [
            ":dart: feat: demo test validate for warning.",
            "",
            "body of commit log",
            "",
        ]
    )
    assert rs == (
        ["The commit message has the required pattern."],
        git.Level.OK,
    )

    rs = git.validate_commit_msg(
        [
            ":dart: feat: demo test validate for warning.",
            "",
            (
                "body of commit log that has character more that 72 and "
                "it will return some warning message from function"
            ),
            "",
        ]
    )
    assert rs == (
        ["The commit body should wrap at 72 characters at line: 3."],
        git.Level.WARNING,
    )
