import datetime as dt
import pathlib
import unittest
from unittest.mock import DEFAULT, patch

from click.testing import CliRunner

import clishelf.emoji as emoji


def side_effect_func(*args, **kwargs):
    if "emoji.py" in args[0]:
        _ = kwargs
        return pathlib.Path(__file__)
    return DEFAULT


class CLIEmojiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()

    def test_ls_emoji(self):
        result = self.runner.invoke(emoji.ls)
        respec = [str(info) for info in emoji.get_emojis()]
        self.assertListEqual(respec, result.output.rstrip("\n").split("\n"))
        self.assertEqual(0, result.exit_code)

    @patch("clishelf.emoji.Path", side_effect=side_effect_func)
    @patch("clishelf.emoji.datetime")
    @patch("clishelf.emoji.requests.get")
    def test_fetch_emoji(self, mock_request, mock_now, mock_path):
        mock_request.get.return_value.json.return_value = []
        mock_now.now.return_value = dt.datetime(2024, 1, 1, 0, 0, 0)
        result = self.runner.invoke(emoji.fetch)
        self.assertTrue(mock_path.called)
        self.assertEqual(0, result.exit_code)

        test_file = pathlib.Path(__file__).parent / "assets/emoji.json"
        self.assertTrue(test_file.exists())

        result = self.runner.invoke(emoji.fetch, args="-b")
        self.assertEqual(0, result.exit_code)

        test_file_bk = (
            pathlib.Path(__file__).parent / "assets/emoji.bk20240101000000.json"
        )
        self.assertTrue(test_file_bk.exists())
        test_file.unlink()
        test_file_bk.unlink()
        test_file_bk.parent.rmdir()
