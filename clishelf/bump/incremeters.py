import re
from collections.abc import Sequence


class NumericIncrementer:
    """Numeric version part incrementer.

    This class handles numeric or alphanumeric version parts and bumps the first
    numeric segment it finds.

    Examples:
        >>> f = NumericIncrementer()
        >>> f.bump("r3")
        'r4'

        - "1" → "2"
        - "r3" → "r4"
        - "r3-001" → "r4-001"

    Args:
        first_value: The starting value (default 0). Must contain at least one digit
            if provided as a string.

    Attributes:
        first_value (str): The starting value.
        optional_value (str): The optional value, equal to `first_value`.
    """

    FIRST_NUMERIC = re.compile(r"(\D*)(\d+)(.*)")

    def __init__(
        self,
        first_value: str | int | None = None,
        independent: bool = False,
    ) -> None:
        if first_value is None:
            first_value = "0"

        first_value = str(first_value)
        if not self.FIRST_NUMERIC.search(first_value):
            raise ValueError(
                f"Invalid first_value '{first_value}': must contain at least "
                f"one digit."
            )

        self.first_value = str(first_value)
        self.optional_value = self.first_value
        self.independent = independent

    def bump(self, value: str) -> str:
        """Increment the numeric portion of the given value."""
        match = self.FIRST_NUMERIC.search(value)
        if not match:
            raise ValueError(
                f"Cannot bump '{value}': no numeric portion found."
            )

        prefix, numeric, suffix = match.groups()
        bumped_numeric = str(int(numeric) + 1)
        return f"{prefix}{bumped_numeric}{suffix}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(first_value={self.first_value!r})"


class ValuesIncrementer:
    """Cyclic version part incrementer based on a fixed set of allowed values.

    Args:
        values: The ordered list of allowed values (must not be empty).
        optional_value: The optional fallback value (defaults to the first value).
        first_value: The starting value (defaults to the first value).

    Raises:
        ValueError: If any provided value is invalid or missing from the list.

    Example:
        >>> f = ValuesIncrementer(["alpha", "beta", "rc", "final"])
        >>> f.bump("beta")
        'rc'
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

    def bump(self, value):
        """Advance to the next value in the list."""
        try:
            current_index = self._values.index(value)
        except ValueError as exc:
            raise ValueError(
                f"Invalid value '{value}': not found in {self._values}"
            ) from exc

        if current_index + 1 >= len(self._values):
            raise ValueError(
                f"'{value}' is already the maximum value in {self._values}."
            )
        return self._values[current_index + 1]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(values={self._values!r}, "
            f"first_value={self.first_value!r}, "
            f"optional_value={self.optional_value!r})"
        )
