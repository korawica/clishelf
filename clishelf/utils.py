# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

try:  # pragma: no cov
    # NOTE: This package already provided at core package for Python v3.11+
    import tomllib
except ModuleNotFoundError:
    # NOTE: Need to install pip if the current venv created from uv.
    #   >>> uv pip install pip
    import pip._vendor.tomli as tomllib


def load_pyproject(file: Optional[str] = None) -> dict[str, Any]:
    """Load Configuration from pyproject.toml file.

    :param file: A file path or string path that keeping the pyproject.toml.

    :rtype: dict[str, Any]
    """
    pyproject: Path = Path(file or "./pyproject.toml")
    if not pyproject.exists():
        return {}

    with pyproject.open(mode="rb") as f:
        return tomllib.load(f)


def load_config() -> dict[str, Any]:
    """Return config of the shelf package that was set on pyproject.toml.

    :rtype: dict[str, Any]
    """
    data: dict[str, Any] = {}

    conf_file: Path = Path(".clishelf.yaml")
    if conf_file.exists():
        data = yaml.safe_load(conf_file.read_text(encoding="utf-8"))

    return {
        **data,
        **load_pyproject().get("tool", {}).get("shelf", {}),
    }


class Bcolors(str, Enum):
    """An Enum for colors using ANSI escape sequences.

    Reference:
        - https://stackoverflow.com/questions/287871
    """

    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_CYAN = "\033[96m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    INFO = "\033[94m"
    ERROR = "\033[91m"


class Level(str, Enum):
    """An Enum for notification levels that relate with Bcolors enum object."""

    OK = "OK"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def make_color(message: str, level: Level, prefix: bool = False) -> str:
    """Print the message with a color for the corresponding level.

    :param message: A message string that want to echo.
    :param level: A level of color.
    :param prefix: A prefix flag for adding level value in message.

    :rtype: str
    """
    return (
        f"{Bcolors[level].value}{Bcolors.BOLD.value}"
        f"{f'{level.value}: ' if prefix else ''}"
        f"{message}{Bcolors.END.value}"
    )


@dataclass(frozen=True)
class Profile:
    """Profile dataclass object for keeping a Git profile data."""

    name: str
    email: str


def prepare_str(context: str) -> str:
    return context.strip().strip("\n").strip("\r")
