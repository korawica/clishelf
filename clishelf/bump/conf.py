from __future__ import annotations

import glob
import logging
import re
import warnings
from configparser import NoOptionError, RawConfigParser
from pathlib import Path
from re import Pattern
from typing import Any

try:  # pragma: no cov
    # NOTE: This package already provided at core package for Python v3.11+
    import tomllib
except ModuleNotFoundError:
    # NOTE: Need to install pip if the current venv created from uv.
    #   >>> uv pip install pip
    import pip._vendor.tomli as tomllib

from .utils import ConfFile
from .version_part import (
    ConfiguredPartConf,
    NumericPartConf,
    VersionConfig,
)

logger = logging.getLogger(__name__)

RE_DETECT_SECTION_TYPE: Pattern[str] = re.compile(
    r"^bumpversion:"
    r"((?P<file>file|glob)(\s*\(\s*(?P<file_suffix>[^):]+)\)?)?|(?P<part>part)):"
    r"(?P<value>.+)",
)


def _read_toml_file(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def _read_ini_file(path: Path) -> dict[str, Any]:
    """
    Read .bumpversion.cfg / setup.cfg-like files into a toml-like dict shape.
    This keeps compatibility with old configparser-based setups (DEPRECATED).
    """
    cp = RawConfigParser()
    cp.optionxform = lambda option: option  # preserve case
    with path.open("rt", encoding="utf-8") as f:
        cp.read_string(f.read())

    out: dict[str, Any] = {}

    # NOTE: bumpversion section: default/flat mapping
    if cp.has_section("bumpversion"):
        defaults: dict[str, Any] = dict(cp.items("bumpversion"))

        # Handle serialize → list
        if "serialize" in defaults:
            value = defaults["serialize"]
            defaults["serialize"] = [
                x.strip() for x in value.splitlines() if x.strip()
            ]

        # Handle boolean options
        for bool_name in ("commit", "tag", "dry_run"):
            try:
                defaults[bool_name] = cp.getboolean("bumpversion", bool_name)
            except NoOptionError:
                pass  # skip missing
            except ValueError:
                # not a valid boolean, keep as string
                pass

        out["bumpversion"] = defaults
    else:
        out["bumpversion"] = {}

    # --- other sections (part/file) ---
    for section in cp.sections():
        if section == "bumpversion":
            continue
        m = RE_DETECT_SECTION_TYPE.match(section)
        if not m:
            continue

        items: dict[str, Any] = dict(cp.items(section))

        # values → list
        if "values" in items:
            items["values"] = [
                x.strip() for x in items["values"].splitlines() if x.strip()
            ]

        # serialize → list
        if "serialize" in items:
            items["serialize"] = [
                x.strip().replace("\\n", "\n")
                for x in items["serialize"].splitlines()
                if x.strip()
            ]

        out[section] = items

    return out


def _discover_config_file(
    explicit: str | Path | None = None,
) -> tuple[Path | None, str]:
    """Determine config file location.

    Prefer bumpversion.toml if present, else fallback to .bumpversion.cfg (deprecated),
    then setup.cfg (deprecated).

    Returns (Path or None, format) where format is 'toml' or 'ini' or 'none'.
    """
    if explicit:
        p = Path(explicit)
        if not p.exists():
            return p, "toml" if p.suffix in (".toml",) else "ini"
        if p.suffix == ".toml":
            return p, "toml"
        else:
            return p, "ini"

    if Path("bumpversion.toml").exists():
        return Path("bumpversion.toml"), "toml"
    if not Path(".bumpversion.cfg").exists() and Path("setup.cfg").exists():
        return Path("setup.cfg"), "ini"
    if Path(".bumpversion.cfg").exists():
        return Path(".bumpversion.cfg"), "ini"
    return None, "none"


def load_config(
    explicit_config: str | Path | None = None,
    defaults: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[ConfFile], dict[str, Any], Path | None, str]:
    """Loads configuration.

    Returns:
      (defaults_map, configured_files, part_configs, config_path, config_format)
        - defaults_map: mapping of bumpversion defaults (serialize, search, replace, etc.)
        - configured_files: list of ConfFile objects (maybe empty)
        - part_configs: dict mapping part name -> VersionPartConfiguration objects
        - config_path: path to the config file used (or None)
        - config_format: 'toml', 'ini', or 'none'
    """
    defaults: dict[str, Any] = defaults or {}
    config_path, config_format = _discover_config_file(explicit_config)

    if config_path is None or config_format == "none":
        logger.info(
            "No configuration file found (looked for bumpversion.toml, "
            ".bumpversion.cfg, setup.cfg)."
        )
        return defaults, [], {}, None, "none"

    if config_format == "toml":
        try:
            raw = _read_toml_file(config_path)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to read TOML config {config_path}: {exc}"
            ) from exc
    else:
        warnings.warn(
            "INI-style bumpversion config (.bumpversion.cfg or setup.cfg) is deprecated. "
            "Please migrate to bumpversion.toml",
            DeprecationWarning,
            stacklevel=2,
        )
        raw = _read_ini_file(config_path)

    defaults.update(raw.get("bumpversion", {}).copy())

    # NOTE: normalize certain keys
    if isinstance(defaults.get("serialize"), str):
        defaults["serialize"] = [
            s for s in defaults["serialize"].splitlines() if s.strip()
        ]

    # NOTE: build part_configs and files
    part_configs: dict[str, Any] = {}
    files: list[ConfFile] = []

    # iterate sections in raw data (toml keys or legacy-named sections)
    for section_key, section_value in raw.items():
        if section_key == "bumpversion":
            continue
        m = RE_DETECT_SECTION_TYPE.match(section_key)
        if not m:
            continue
        gd = m.groupdict()
        section_val = gd["value"]
        section_config = (
            dict(section_value) if isinstance(section_value, dict) else {}
        )
        # NOTE: If it's a part
        if gd.get("part"):
            vs_part_conf = NumericPartConf
            if "values" in section_config:
                vs_part_conf = ConfiguredPartConf
            if "independent" in section_config:
                # configparser returns string "True"/"False" in legacy flow, but toml returns bool
                if isinstance(section_config["independent"], str):
                    section_config["independent"] = section_config[
                        "independent"
                    ].lower() in ("1", "true", "yes")
                else:
                    section_config["independent"] = bool(
                        section_config["independent"]
                    )
            part_configs[section_val] = vs_part_conf(**section_config)
        elif gd.get("file"):
            filename = section_val
            if "parse" not in section_config:
                section_config["parse"] = defaults.get(
                    "parse", r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
                )
            if "serialize" not in section_config:
                section_config["serialize"] = defaults.get(
                    "serialize", ["{major}.{minor}.{patch}"]
                )
            if "search" not in section_config:
                section_config["search"] = defaults.get(
                    "search", "{current_version}"
                )
            if "replace" not in section_config:
                section_config["replace"] = defaults.get(
                    "replace", "{new_version}"
                )

            # NOTE: ensure serialize is list
            if isinstance(section_config.get("serialize"), str):
                section_config["serialize"] = [
                    line
                    for line in section_config["serialize"].splitlines()
                    if line.strip()
                ]

            # NOTE: include part_configs reference
            section_config["part_configs"] = part_configs

            version_config = VersionConfig(**section_config)
            if gd.get("file") == "glob":
                for fn in glob.glob(filename, recursive=True):
                    files.append(ConfFile(fn, version_config))
            else:
                files.append(ConfFile(filename, version_config))

    return defaults, files, part_configs, config_path, config_format


def save_config(
    config_path: Path | None,
    config_format: str,
    defaults: dict[str, Any],
    new_version: str,
    dry_run: bool = False,
) -> None:
    """Update the config file to set bumpversion.current_version = new_version.

    Behavior:
      - If config_format == 'toml' and tomli_w is available, write TOML.
      - If config_format == 'ini', update .bumpversion.cfg using ConfigParser (legacy behavior).
      - If config_path is None, raise.
    """
    try:  # pragma: no cov
        import tomli_w
    except ImportError as err:
        raise RuntimeError(
            "tomli-w is required for writing TOML on Python <3.11"
        ) from err

    if config_path is None:
        raise RuntimeError(
            "No configuration file path provided to save_config."
        )

    if dry_run:
        logger.info(
            "Dry-run: would write new version %s into %s",
            new_version,
            config_path,
        )
        return

    if config_format != "toml":
        # NOTE: legacy INI write: read current file and write updated
        #   bumpversion.current_version
        cp = RawConfigParser()
        cp.optionxform = lambda option: option
        with config_path.open("rt", encoding="utf-8") as fh:
            data = fh.read()
        cp.read_string(data)
        if not cp.has_section("bumpversion"):
            cp.add_section("bumpversion")
        cp.set("bumpversion", "current_version", new_version)
        # NOTE: write back using the original newline behavior
        with config_path.open("wt", encoding="utf-8", newline="") as fh:
            cp.write(fh)

    # NOTE: Build a minimal bumpversion table and write it; preserve any unknown
    #   top-level keys is out-of-scope.
    toml_obj = {"bumpversion": dict(defaults or {})}
    toml_obj["bumpversion"]["current_version"] = new_version
    with config_path.open("wb") as f:
        tomli_w.dump(toml_obj, f)
