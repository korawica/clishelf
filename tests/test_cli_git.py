import datetime as dt
import subprocess
import sys
import unittest
from unittest.mock import DEFAULT, MagicMock, patch

from click.testing import CliRunner

import clishelf.git as git


def side_effect_func(*args, **kwargs):
    if any(["git", "rev-parse", "--abbrev-ref", "HEAD"] == a for a in args):
        _ = kwargs
        return "0.1.2".encode(encoding=sys.stdout.encoding)
    elif any(["git", "describe", "--tags", "--abbrev=0"] == a for a in args):
        _ = kwargs
        return "v0.0.1".encode(encoding=sys.stdout.encoding)
    else:
        return DEFAULT


class CLIGitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_cli_branch_name(self, mock):
        result = self.runner.invoke(git.bn)
        self.assertTrue(mock.called)
        self.assertEqual("0.1.2\n", result.output)
        self.assertEqual(0, result.exit_code)

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_cli_latest_tag(self, mock):
        result = self.runner.invoke(git.tg)
        self.assertTrue(mock.called)
        self.assertEqual("v0.0.1\n", result.output)
        self.assertEqual(0, result.exit_code)


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
            refs="",
            date=dt.datetime(2021, 1, 1),
            msg=git.CommitMsg(content="test: test commit message", body="|"),
            author="Demo Username",
        )
        self.assertEqual(
            ":test_tube: test: test commit message",
            commit_log.msg.content,
        )

    @patch("clishelf.git.subprocess.check_output")
    def test_get_branch_name(self, mock):
        mock_stdout = MagicMock()
        mock_stdout.configure_mock(**{"decode.return_value": "0.0.1"})
        mock.return_value = mock_stdout

        # Start Test after mock subprocess.
        result = git.get_branch_name()
        self.assertEqual("0.0.1", result)

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_get_branch_name_with_side_effect(self, mock):
        # Start Test after mock subprocess.
        result = git.get_branch_name()
        self.assertTrue(mock.called)
        self.assertEqual("0.1.2", result)

    @patch(
        "clishelf.git.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(
            1,
            cmd="git",
            stderr="Error message from command git.",
        ),
    )
    def test_get_branch_name_raise(self, mock):
        with self.assertRaises(subprocess.CalledProcessError) as exc:
            git.get_branch_name()

        # Start Test after mock subprocess.
        self.assertTrue(mock.called)
        self.assertEqual(
            "Error message from command git.",
            str(exc.exception.stderr),
        )
        self.assertEqual("1", str(exc.exception.returncode))

    @patch("clishelf.git.subprocess.check_output", side_effect=side_effect_func)
    def test_get_latest_tag(self, mock):
        # Start Test after mock subprocess.
        result = git.get_latest_tag()
        self.assertTrue(mock.called)
        self.assertEqual("v0.0.1", result)

    @patch(
        "clishelf.git.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "git"),
    )
    @patch("clishelf.__about__.__version__", "0.0.9")
    def test_get_latest_tag_raise(self, mock):
        # Start Test after mock subprocess.
        result = git.get_latest_tag()
        self.assertTrue(mock.called)
        self.assertEqual("v0.0.9", result)

        with self.assertRaises(RuntimeError):
            git.get_latest_tag(default=False)
