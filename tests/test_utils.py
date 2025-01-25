import pathlib
from unittest.mock import DEFAULT, patch

import clishelf.utils as utils


def side_effect_func(*args, **kwargs):
    if "pyproject.toml" in args[0]:
        _ = kwargs
        return pathlib.Path(__file__).parent.parent / "pyproject.toml"
    elif ".clishelf.yaml" in args[0]:
        return pathlib.Path(__file__).parent / ".clishelf.yaml"
    return DEFAULT


def side_effect_func_pyproject(*args, **kwargs):
    _ = kwargs

    if "pyproject.toml" in args[0]:
        return pathlib.Path(__file__).parent.parent / "not-exist-pyproject.toml"

    return DEFAULT


def test_make_color():
    result = utils.make_color("test", utils.Level.OK)
    assert result == "\x1b[92m\x1b[1mOK: test\x1b[0m"


@patch("clishelf.utils.Path", side_effect=side_effect_func_pyproject)
def test_load_pyproject(mock_path):
    data = utils.load_pyproject()
    assert data == {}


@patch("clishelf.utils.Path", side_effect=side_effect_func)
@patch("clishelf.utils.load_pyproject")
def test_load_config(mock_load_pyproject, mock_path):
    mock_load_pyproject.return_value = {}
    data = utils.load_config()
    assert {} == data

    main_file = pathlib.Path(__file__).parent / ".clishelf.yaml"
    with main_file.open(mode="w") as f:
        f.writelines(
            [
                "git:\n",
                "  commit_prefix:\n",
                '    - ["comment", "Documents", ":bulb:"]\n',
            ]
        )
    data = utils.load_config()
    assert {
        "git": {"commit_prefix": [["comment", "Documents", ":bulb:"]]}
    } == data
    main_file.unlink()
