from enum import Enum
from pathlib import Path
from typing import Any, Dict

import tomli


def pwd() -> Path:
    return Path(".")


def load_pyproject() -> Dict[str, Any]:
    """Load Configuration from pyproject.toml file."""
    pyproject: Path = Path("pyproject.toml")
    return tomli.loads(pyproject.read_text()) if pyproject.exists() else {}


def ls(path: str):
    yield from pwd().glob(path)


def readline(path: str):
    file = pwd() / Path(path)
    return file.read_text(encoding="utf-8")


class Bcolors(str, Enum):
    """A Enum for colors using ANSI escape sequences.
    Reference:
    - https://stackoverflow.com/questions/287871

    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    OK = "\033[92m"
    INFO = "\033[94m"
    ERROR = "\033[91m"


class Level(str, Enum):
    """An Enum for notification levels."""

    OK = "OK"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def make_color(message: str, level: Level) -> str:
    """Print the message with a color for the corresponding level."""
    return f"{Bcolors[level]}{Bcolors.BOLD}{level}: {message}{Bcolors.ENDC}"
