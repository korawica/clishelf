from datetime import datetime
from pathlib import Path
from unittest.mock import DEFAULT, patch

from click.testing import CliRunner

import clishelf.emoji as emoji


def side_effect_func(*args, **kwargs):
    if "emoji.py" in args[0]:
        _ = kwargs
        return Path(__file__)
    return DEFAULT


@patch("clishelf.emoji.Path", side_effect=side_effect_func)
@patch("clishelf.emoji.datetime")
@patch("clishelf.emoji.requests.get")
def test_fetch_emoji(mock_request, mock_now, mock_path):
    runner = CliRunner()

    mock_request.get.return_value.json.return_value = []
    mock_now.now.return_value = datetime(2024, 1, 1, 0, 0, 0)
    result = runner.invoke(emoji.fetch)
    assert mock_path.called
    assert 0 == result.exit_code

    test_file: Path = Path(__file__).parent / "assets/emoji.json"
    assert test_file.exists()

    result = runner.invoke(emoji.fetch, args="-b")
    assert result.exit_code == 0

    test_file_bk = Path(__file__).parent / "assets/emoji.bk20240101000000.json"
    assert test_file_bk.exists()

    test_file.unlink()
    test_file_bk.unlink()
    test_file_bk.parent.rmdir()
