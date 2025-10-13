from __future__ import annotations

import logging
import re
import string
from collections.abc import Iterator
from typing import Any

try:  # pragma: no cov
    from typing import Self
except ImportError:
    from typing_extensions import Self

from ..errors import (
    IncompleteVersionRepresentationException,
    MissingValueForSerializationException,
)
from ..utils import kv_str
from .incremeters import NumericIncrementer, ValuesIncrementer

logger = logging.getLogger(__name__)


class PartConf:
    """Base class for version part behavior configuration."""

    function_cls = NumericIncrementer

    def __init__(self, *args, **kwargs) -> None:
        self.function = self.function_cls(*args, **kwargs)

    @property
    def first_value(self) -> str:
        return str(self.function.first_value)

    @property
    def optional_value(self) -> str:
        return str(self.function.optional_value)

    def bump(self, value: str) -> str:
        """Increment or otherwise transform the given version value."""
        return self.function.bump(value)


class ConfiguredPartConf(PartConf):
    """Configuration using a predefined set of values."""

    function_cls = ValuesIncrementer


class NumericPartConf(PartConf):
    """Configuration using numeric increment logic."""

    function_cls = NumericIncrementer


class VersionPart:
    """Represents a single part of a version (e.g., major, minor, patch)."""

    __slots__ = ("_value", "config")

    def __init__(
        self,
        value: str | None,
        config: PartConf | None,
    ) -> None:
        self._value: str | None = value
        self.config: PartConf = config or NumericPartConf()

    @property
    def value(self) -> str:
        """Return value, using the optional fallback if not set."""
        return self._value or self.config.optional_value

    def bump(self) -> Self:
        """Return a new VersionPart incremented according to its configuration."""
        return VersionPart(self.config.bump(self.value), self.config)

    def null(self) -> Self:
        """Reset the part to its first value."""
        return VersionPart(self.config.first_value, self.config)

    def copy(self) -> Self:
        """Return a shallow copy."""
        return VersionPart(self._value, self.config)

    def is_optional(self) -> bool:
        return self.value == self.config.optional_value

    def __repr__(self) -> str:
        return f"<VersionPart {self.config.__class__.__name__}:{self.value}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __format__(self, format_spec: str) -> str:
        return self.value


class Version:
    """Represents an entire version composed of multiple parts."""

    def __init__(
        self,
        values: dict[str, VersionPart],
        original: str | None = None,
    ):
        self.values: dict[str, VersionPart] = dict(values)
        self.original: str | None = original

    def __getitem__(self, key: str) -> VersionPart:
        return self.values[key]

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __repr__(self) -> str:
        return f"<Version {kv_str(self.values)}>"

    def bump(self, part_name: str, order: Iterator[str] | list[str]) -> Self:
        """Return a new Version with the specified part bumped."""
        bumped: bool = False
        new_values: dict[str, VersionPart] = {}

        for label in order:
            if label not in self.values:
                continue

            part = self.values[label]
            if label == part_name:
                new_values[label] = part.bump()
                bumped = True
            elif bumped:
                new_values[label] = part.null()
            else:
                new_values[label] = part.copy()

        return Version(new_values, original=self.original)


def labels_for_format(serialize_format: str) -> list[str]:
    """Extract field names from a format string.

    Examples:
        >>> labels_for_format("{major}.{minor}.{patch}")
        ['major', 'minor', 'patch']

    Returns:
        list[str]: A list of format label name.
    """
    return [
        label
        for _, label, _, _ in string.Formatter().parse(serialize_format)
        if label
    ]


class VersionConfig:
    """Holds a complete representation of a version string and its behavior."""

    def __init__(
        self,
        parse: str,
        serialize: list[str],
        search: str,
        replace: str,
        part_configs: dict[str, PartConf] | None = None,
    ) -> None:
        try:
            self.parse_regex = re.compile(parse, re.VERBOSE)
        except re.error as err:
            logger.error("Invalid regex in --parse: %s", parse)
            raise err

        self.serialize_formats: list[str] = serialize
        self.part_configs: dict[str, PartConf] = part_configs or {}
        self.search: str = search
        self.replace: str = replace

    def order(self) -> list[str]:
        """Return the order of version labels based on the first serialize
        format.

        Returns:
            list[str]: A result for a labels_for_format function.
        """
        return labels_for_format(self.serialize_formats[0])

    def parse(self, version_string: str) -> Version | None:
        """Parse a version string into VersionParts."""
        if not version_string:
            return None

        if not (match := self.parse_regex.search(version_string)):
            logger.warning(f"Failed to parse version: '{version_string}'")
            return None

        parts: dict[str, VersionPart] = {
            k: VersionPart(v, self.part_configs.get(k))
            for k, v in match.groupdict().items()
        }

        version = Version(parts, original=version_string)
        logger.debug(f"Parsed version: {kv_str(version.values)}")
        return version

    @staticmethod
    def _serialize(
        version: Version,
        serialize_format: str,
        context: dict[str, Any],
        raise_if_incomplete: bool = False,
    ) -> str:
        """Serialize the given version using the specified format."""
        values = {**context, **version.values}

        try:
            serialized = serialize_format.format(**values)
        except KeyError as e:
            raise MissingValueForSerializationException(
                f"Missing key {e.args[0]!r} while serializing {version!r}"
            ) from e

        if raise_if_incomplete:
            required_labels = set(labels_for_format(serialize_format))
            present_labels = {
                k for k, v in values.items() if isinstance(v, VersionPart)
            }
            missing = required_labels - present_labels
            if missing:
                raise IncompleteVersionRepresentationException(
                    f"Could not represent {missing} in format {serialize_format}"
                )

        return serialized

    def _choose_serialize_format(
        self, version: Version, context: dict[str, Any]
    ) -> str:
        """Select the most appropriate serialization format."""
        for fmt in self.serialize_formats:
            try:
                self._serialize(version, fmt, context, raise_if_incomplete=True)
                return fmt
            except IncompleteVersionRepresentationException:
                continue
        raise KeyError("No valid serialization format found")

    def serialize(self, version: Version, context: dict[str, Any]) -> str:
        """Serialize the version into a string."""
        fmt: str = self._choose_serialize_format(version, context)
        serialized = self._serialize(version, fmt, context)
        logger.debug("Serialized version to '%s'", serialized)
        return serialized
