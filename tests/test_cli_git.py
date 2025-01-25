import datetime as dt
import subprocess
import sys
from unittest.mock import DEFAULT, patch

import clishelf.git as git
from clishelf.utils import Profile


def side_effect_func(*args, **kwargs):
    if any(["git", "rev-parse", "--abbrev-ref", "HEAD"] == a for a in args):
        _ = kwargs
        return "0.1.2".encode(encoding=sys.stdout.encoding)
    elif any(["git", "describe", "--tags", "--abbrev=0"] == a for a in args):
        _ = kwargs
        return "v0.0.1".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


def test_commit_message():
    msg = git.CommitMsg(content="test: test commit message", body="")
    assert ":test_tube: test: test commit message" == msg.content
    assert "Code Changes" == msg.mtype


def test_commit_log():
    commit_log = git.CommitLog(
        hash="",
        refs="",
        date=dt.datetime(2021, 1, 1),
        msg=git.CommitMsg(content="test: test commit message", body="|"),
        author=Profile(name="Demo Username", email="demo@mail.com"),
    )
    assert ":test_tube: test: test commit message" == commit_log.msg.content


@patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
def test_get_latest_tag(mock):
    result = git.get_latest_tag()
    assert mock.called
    assert "v0.0.1" == result


@patch(
    "clishelf.git.subprocess.check_output",
    side_effect=subprocess.CalledProcessError(1, "git"),
)
def test_get_latest_tag_raise(mock):
    # Start Test after mock subprocess.
    result = git.get_latest_tag()
    assert mock.called
    assert "v0.0.0" == result
