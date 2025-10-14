from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import datetime
from re import Match, Pattern

from .utils import get_datetime_info


class PartIncrementer:
    """Base class for a version part function."""

    first_value: str
    optional_value: str
    independent: bool
    always_increment: bool

    def bump(self, value: str) -> str:
        """Increase the value."""
        raise NotImplementedError(
            "Part function should implement the bump method."
        )


class IndependentIncrementer(PartIncrementer):
    """This is a class that provides an independent function for version parts.

    It simply returns the optional value, which is equal to the first value.
    """

    def __init__(self, value: str | int | None = None):
        if value is None:
            value: str = ""
        self.first_value = str(value)
        self.optional_value = str(value)
        self.independent = True
        self.always_increment = False

    def bump(self, value: str | None = None) -> str:
        """Return the optional value."""
        return value or self.optional_value


class CalVerIncrementer(PartIncrementer):
    """This is a class that provides a CalVer function for version parts."""

    def __init__(self, calver_format: str):
        self.independent = False
        self.calver_format = calver_format
        self.first_value = self.bump()
        self.optional_value = "There isn't an optional value for CalVer."
        self.independent = False
        self.always_increment = True

    def bump(self, value: str | None = None) -> str:
        """Return the optional value."""
        return self.calver_format.format(**get_datetime_info(datetime.now()))


class NumericIncrementer(PartIncrementer):
    """Numeric version part incrementer.

    This class handles numeric or alphanumeric version parts and bumps the first
    numeric segment it finds.

    Examples:
        >>> f = NumericIncrementer()
        >>> f.bump("r3")
        'r4'
        >>> f.bump("1")
        '2'
        >>> f.bump("r3-001")
        'r4-001'

    Args:
        first_value (str | int | None):
            The starting value (default 0). Must contain at least one digit if
            provided as a string.
        independent (bool, default False):
            An independent flag.

    Attributes:
        first_value (str): The starting value.
        optional_value (str): The optional value, equal to `first_value`.
    """

    FIRST_NUMERIC: Pattern[str] = re.compile(r"(\D*)(\d+)(.*)")

    def __init__(
        self,
        first_value: str | int | None = None,
        independent: bool = False,
    ) -> None:
        if first_value is None:
            first_value: str = "0"

        first_value: str = str(first_value)
        if not self.FIRST_NUMERIC.search(first_value):
            raise ValueError(
                f"Invalid first_value {first_value!r}: must contain at least "
                f"one digit."
            )

        self.first_value = str(first_value)
        self.optional_value = self.first_value
        self.independent: bool = independent
        self.always_increment: bool = False

    def bump(self, value: str) -> str:
        """Increment the numeric portion of the given value.

        Args:
            value (str): A string value that want to increase number by 1.
        """
        match: Match[str] | None = self.FIRST_NUMERIC.search(value)
        if not match:
            raise ValueError(
                f"Cannot bump '{value}': no numeric portion found."
            )

        prefix, numeric, suffix = match.groups()

        if int(numeric) < int(self.first_value):
            raise ValueError(
                f"The given value {value} is lower than the first "
                f"value {self.first_value} and cannot be bumped."
            )

        bumped_numeric: str = str(int(numeric) + 1)
        return f"{prefix}{bumped_numeric}{suffix}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(first_value={self.first_value!r})"


class ValuesIncrementer(PartIncrementer):
    """Cyclic version part incrementer based on a fixed set of allowed values.

    Args:
        values (Sequence[str] | Sequence[int]):
            The ordered list of allowed values (must not be empty).
        optional_value (str | int):
            The optional fallback value (defaults to the first value).
        first_value: The starting value.

    Raises:
        ValueError: If any provided value is invalid or missing from the list.

    Example:
        >>> f = ValuesIncrementer(["alpha", "beta", "rc", "final"])
        >>> f.bump("beta")
        'rc'
        >>> f.bump("final")
        Traceback (most recent call last):
            ...
        ValueError: 'final' is already the maximum value in ['alpha', 'beta', 'rc', 'final'].
    """

    def __init__(
        self,
        values: Sequence[str] | Sequence[int],
        optional_value: str | int | None = None,
        first_value: str | int | None = None,
        independent: bool = False,
    ) -> None:
        if not values:
            raise ValueError("Version part values cannot be empty.")

        self._values: list[str] = list(values)

        if optional_value is None:
            optional_value = values[0]

        self.optional_value = optional_value or self._values[0]
        if self.optional_value not in values:
            raise ValueError(
                f"optional_value '{self.optional_value}' must be included in "
                f"{self._values}"
            )

        self.first_value = first_value or self._values[0]
        if self.first_value not in self._values:
            raise ValueError(
                f"first_value '{self.first_value}' must be included in "
                f"{self._values}"
            )

        self.independent = independent
        self.always_increment = False

    def bump(self, value: str | int) -> str | int:
        """Advance to the next value in the list.

        Args:
            value (str | int): A string or integer value.
        """
        try:
            return self._values[self._values.index(value) + 1]
        except IndexError as e:
            raise ValueError(
                f"The part has already the maximum value among "
                f"{self._values} and cannot be bumped."
            ) from e

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(values={self._values!r}, "
            f"first_value={self.first_value!r}, "
            f"optional_value={self.optional_value!r})"
        )
