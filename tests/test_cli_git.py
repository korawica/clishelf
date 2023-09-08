import contextlib
import datetime as dt
import re
import subprocess
import sys
import unittest
from typing import Callable, NamedTuple, Union
from unittest.mock import DEFAULT, MagicMock, patch

from click.testing import CliRunner

import clishelf.git as git


class CmdMatch(NamedTuple):
    cmd: str
    match: str = ".*"
    result: str = ""
    side_effect: Callable = None


@contextlib.contextmanager
def mock_run(*cmd_match: Union[str, CmdMatch], **kws):
    sub_run = subprocess.run
    mock = MagicMock()
    if isinstance(cmd_match[0], str):
        cmd_match = [CmdMatch(*cmd_match, **kws)]

    def new_run(cmd, **_kws):
        check_cmd = " ".join(cmd[1:])
        mock(*cmd[1:])
        for m in cmd_match:
            if m.cmd in cmd[0].lower() and re.match(m.match, check_cmd):
                if m.side_effect:
                    m.side_effect()
                return subprocess.CompletedProcess(cmd, 0, m.result, "")
        raise AssertionError("No matching call for %s" % check_cmd)

    subprocess.run = new_run
    yield mock
    subprocess.run = sub_run


def side_effect_func(*args, **kwargs):
    if any(["git", "rev-parse", "--abbrev-ref", "HEAD"] == arg for arg in args):
        _ = kwargs
        return "0.0.1".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


class CLIGitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()


class GitTestCase(unittest.TestCase):
    def test_commit_message(self):
        msg = git.CommitMsg(content="test: test commit message", body="")
        self.assertEqual(
            ":test_tube: test: test commit message",
            msg.content,
        )
        self.assertEqual(
            "Code Changes",
            msg.mtype,
        )

    def test_commit_log(self):
        commit_log = git.CommitLog(
            hash="",
            date=dt.datetime(2021, 1, 1),
            msg=git.CommitMsg(content="test: test commit message", body="|"),
            author="Demo Username",
        )
        self.assertEqual(
            ":test_tube: test: test commit message",
            commit_log.msg.content,
        )

    @patch("clishelf.git.subprocess.check_output")
    def test_get_branch_name(self, mock_run):
        mock_stdout = MagicMock()
        mock_stdout.configure_mock(**{"decode.return_value": "0.0.1"})
        mock_run.return_value = mock_stdout
        result = git.get_branch_name()
        self.assertEqual("0.0.1", result)

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_get_branch_name_2(self, mock_run):
        result = git.get_branch_name()
        self.assertTrue(mock_run.called)
        self.assertEqual("0.0.1", result)

    # @patch(
    #     "clishelf.git.subprocess.check_output",
    #     side_effect=subprocess.CalledProcessError(
    #         1, cmd="git", stderr="Test raise"
    #     )
    # )
    # def test_get_data_invalid(self, mock_run):
    #     with self.assertRaises(subprocess.CalledProcessError) as exc:
    #         print(git.get_latest_tag())
    #     print(exc)
