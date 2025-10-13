from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .version_part import VersionConfig

logger = logging.getLogger(__name__)


@dataclass
class ConfFile:
    """Represents a file described in the config.

    Attributes:
      path (Path | str): Path to file on disk
      version_config (VersionConfig): Instance of VersionConfig that provides
        .search, .replace templates and .parse/serialize logic.
    """

    path: str | Path
    version_config: VersionConfig

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path):
            self.path = Path(self.path)

    def __str__(self) -> str:
        return f"{self.path}"

    def should_contain_version(
        self,
        current_version: str,
        context: dict[str, Any],
    ) -> None:
        """Confirm that the file contains the templated search string for current_version.
        Raises ValueError if not found, matching original behavior.

        Args:
            current_version (str): The current version string.
            context:
        """
        if not self.path.exists():
            raise FileNotFoundError(
                f"Configured file '{self.path}' does not exist"
            )

        text: str = self.path.read_text(encoding="utf-8")
        search_template = self.version_config.search

        try:
            search = search_template.format(
                current_version=current_version, **context
            )
        except Exception as err:
            logger.warning(f"Fallback search: {err}")
            # NOTE: fallback: try replacing {current_version} only
            search = search_template.replace(
                "{current_version}", str(current_version)
            )

        if search not in text:
            raise ValueError(
                f"File {self.path} does not contain expected search pattern: "
                f"{search}"
            )

    def replace(
        self,
        current_version: str,
        new_version: str,
        context: dict[str, Any],
        dry_run: bool = False,
    ) -> None:
        """Replace occurrences of version in file according to
        version_config.search / replace.

        Behavior:
          - Build `search` template from version_config.search.format(current_version=..., **context)
          - Build `replace` template from version_config.replace.format(new_version=..., **context)
          - Replace all occurrences (str.replace) in the file text.
        """
        if not self.path.exists():
            raise FileNotFoundError(
                f"Configured file '{self.path}' does not exist"
            )

        text = self.path.read_text(encoding="utf-8")
        search_template = self.version_config.search
        replace_template = self.version_config.replace

        try:
            search = search_template.format(
                current_version=current_version, **context
            )
            replace = replace_template.format(
                new_version=new_version, **context
            )
        except Exception:
            # best-effort fallback
            search = search_template.replace(
                "{current_version}", current_version
            )
            replace = replace_template.replace("{new_version}", new_version)

        if search == replace:
            logger.debug(
                f"[{self.path}] search == replace ({search}); skipping"
            )
            return

        if search not in text:
            raise ValueError(
                f"File {self.path} does not contain search text '{search}'"
            )

        new_text = text.replace(search, replace)
        logger.info(f"[{self.path}] Replace: {search} → {replace}")

        if dry_run:
            logger.debug(f"[{self.path}] Dry run enabled; not writing file.")
            return

        self.path.write_text(new_text, encoding="utf-8")
        logger.debug(f"[{self.path}] Wrote updated content")


def kv_str(d: Any) -> str:
    """Helper to format dict -> readable string (keeps original behaviour)."""
    if not isinstance(d, dict):
        return str(d)
    return ", ".join(f"{k}={v}" for k, v in d.items())


def prefixed_env(prefix: str = "BUMP_") -> dict[str, str]:
    """Return environment variables starting with `prefix` (default BUMP_),
    with prefix stripped, lowercased keys — like original helper.
    """
    out = {}
    for k, v in os.environ.items():
        if k.startswith(prefix):
            out[k[len(prefix) :].lower()] = v
    return out
