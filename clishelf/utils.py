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
except ModuleNotFoundError:
    import pip._vendor.tomli as tomllib

import yaml


def load_pyproject(file: Optional[str] = None) -> dict[str, Any]:
    """Load Configuration from pyproject.toml file."""
    f: str = file or "pyproject.toml"
    pyproject: Path = Path(f)
    if not pyproject.exists():
        return {}
    with pyproject.open(mode="rb") as f:
        return tomllib.load(f)


def load_config() -> dict[str, Any]:
    """Return config of the shelf package that was set on pyproject.toml."""

    data: dict[str, Any] = {}
    conf_file = Path(".clishelf.yaml")
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


def make_color(message: str, level: Level) -> str:
    """Print the message with a color for the corresponding level."""
    return (
        f"{Bcolors[level].value}{Bcolors.BOLD.value}{level.value}: "
        f"{message}{Bcolors.END.value}"
    )


@dataclass(frozen=True)
class Profile:
    name: str
    email: str
