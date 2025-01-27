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

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cov
    import pip._vendor.tomli as tomllib

import yaml


def load_pyproject(file: Optional[str] = None) -> dict[str, Any]:
    """Load Configuration from pyproject.toml file.

    :param file: A file path or string path that keeping the pyproject.toml.

    :rtype: dict[str, Any]
    """
    f: str = file or "./pyproject.toml"
    pyproject: Path = Path(f)

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

    HEADER: str = "\033[95m"
    OK_BLUE: str = "\033[94m"
    OK_CYAN: str = "\033[96m"
    OK_GREEN: str = "\033[92m"
    WARNING: str = "\033[93m"
    FAIL: str = "\033[91m"
    END: str = "\033[0m"
    BOLD: str = "\033[1m"
    OK: str = "\033[92m"
    INFO: str = "\033[94m"
    ERROR: str = "\033[91m"


class Level(str, Enum):
    """An Enum for notification levels that relate with Bcolors enum object."""

    OK: str = "OK"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    ERROR: str = "ERROR"


def make_color(message: str, level: Level) -> str:
    """Print the message with a color for the corresponding level.

    :param message: A message string that want to echo.
    :param level: A level of color.

    :rtype: str
    """
    return (
        f"{Bcolors[level].value}{Bcolors.BOLD.value}{level.value}: "
        f"{message}{Bcolors.END.value}"
    )


@dataclass(frozen=True)
class Profile:
    """Profile dataclass object for keeping a Git profile data."""

    name: str
    email: str


def prepare_str(context: str) -> str:
    return context.strip().strip("\n").strip("\r")
