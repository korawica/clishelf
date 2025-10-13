from __future__ import annotations

import logging
import sys
from typing import Any, Final, Optional

import click

from .bump import (
    assemble_context,
    bump_version_by_part_or_literal,
    check_files_contain_version,
    commit_and_tag_if_required,
    determine_vcs_dirty,
    determine_vcs_usability,
    replace_version_in_files,
)
from .conf import load_config, save_config
from .utils import ConfFile
from .version_part import VersionConfig

logger = logging.getLogger(__name__)
log_formatter = logging.Formatter("%(message)s")
ch = logging.StreamHandler(sys.stderr)
ch.setFormatter(log_formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)

DEFAULT_MESSAGE: Final[str] = "Bump version: {current_version} → {new_version}"


@click.group()
@click.option("--verbose", "-v", count=True, help="increase verbosity")
@click.option(
    "--list",
    "show_list",
    is_flag=True,
    default=False,
    help="List machine readable information",
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, show_list: bool):
    """bump2version — manage & update project version strings."""
    # set log level
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, verbose)]
    logger.setLevel(level)
    ctx.obj = {"show_list": show_list, "verbose": verbose}


@cli.command("bump")
@click.argument("part", required=False)
@click.argument("files", nargs=-1)
@click.option(
    "--config-file",
    "-c",
    "config_file",
    type=click.Path(),
    default=None,
    help="Config file to use (default: bumpversion.toml or .bumpversion.cfg)",
)
@click.option(
    "--current-version",
    "-C",
    "current_version",
    required=False,
    help="Version that needs to be updated",
)
@click.option(
    "--new-version",
    "-N",
    "new_version",
    required=False,
    help="New version string (overrides bumping)",
)
@click.option(
    "--dry-run", "-n", is_flag=True, help="Don't write any files, just pretend."
)
@click.option(
    "--no-configured-files",
    is_flag=True,
    default=False,
    help="Ignore files listed in config; only use files passed on CLI",
)
@click.option(
    "--allow-dirty",
    is_flag=True,
    default=False,
    help="Don't abort if working directory is dirty",
)
@click.option(
    "--commit/--no-commit",
    default=None,
    help="Commit changes to version control",
)
@click.option(
    "--tag/--no-tag", default=None, help="Create a tag in version control"
)
@click.option(
    "--sign-tags/--no-sign-tags", default=None, help="Sign tags if created"
)
@click.option("--tag-name", default="v{new_version}", help="Tag name")
@click.option(
    "--tag-message",
    default="Bump version: {current_version} → {new_version}",
    help="Tag message",
)
@click.option(
    "--message",
    "-m",
    default="Bump version: {current_version} → {new_version}",
    help="Commit message",
)
@click.option(
    "--commit-args",
    default="",
    help="Extra args passed to commit command (multiple lines allowed)",
)
@click.option("--parse", default=None, help="Override parse regex")
@click.option(
    "--serialize",
    default=None,
    help="Override serialize (single template or newline separated)",
)
@click.option("--search", default=None, help="Override search template")
@click.option("--replace", default=None, help="Override replace template")
@click.pass_obj
def bump(
    obj: dict[str, Any],
    part: Optional[str],
    files: list[str],
    config_file: Optional[str],
    current_version: Optional[str],
    new_version: Optional[str],
    dry_run: bool,
    no_configured_files: bool = False,
    allow_dirty: bool = False,
    commit: Optional[bool] = None,
    tag: Optional[bool] = None,
    sign_tags: Optional[bool] = None,
    tag_name: str = "v{new_version}",
    tag_message: str = DEFAULT_MESSAGE,
    message: str = DEFAULT_MESSAGE,
    commit_args: str = "",
    parse: Optional[str] = None,
    serialize: Optional[str] = None,
    search: Optional[str] = None,
    replace: Optional[str] = None,
):
    """Bump a part of the version and update configured files.

    Usage:

      bump2version bump <part> [file1 file2 ...] [options]

    If new-version passed with --new-version it will be used as-is.
    """
    # NOTE: load configuration
    defaults, configured_files, part_configs, cfg_path, cfg_format = (
        load_config(config_file)
    )

    # NOTE: CLI overrides
    if parse:
        defaults["parse"] = parse
    if serialize:
        # allow newline separated or single template
        if "\n" in serialize:
            defaults["serialize"] = [
                i for i in serialize.splitlines() if i.strip()
            ]
        else:
            defaults["serialize"] = [serialize]
    if search:
        defaults["search"] = search
    if replace:
        defaults["replace"] = replace

    # build VersionConfig to use for CLI-run files
    vc = VersionConfig(
        parse=defaults.get(
            "parse", r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
        ),
        serialize=defaults.get("serialize", ["{major}.{minor}.{patch}"]),
        search=defaults.get("search", "{current_version}"),
        replace=defaults.get("replace", "{new_version}"),
        part_configs=part_configs,
    )

    # explicit current_version required (like original) if not in defaults
    if not current_version:
        current_version: str = defaults.get("current_version")
    if not current_version:
        raise click.UsageError(
            "The current_version must be provided via --current-version or "
            "config file."
        )

    # prepare list of files to change
    target_files = []
    if files:
        for filename in files:
            target_files.append(filename)
    if not no_configured_files:
        # use configured files from config (ConfiguredFile objects)
        # merge CLI-specified files to preserve order and override if any
        for cf in configured_files:
            target_files.append(str(cf.path))

    final_files: list[ConfFile] = []
    if not no_configured_files:
        final_files.extend(configured_files)
    # Add files passed explicitly and not already in configured_files
    existing_paths = {str(f.path) for f in final_files}
    for f in files:
        if f not in existing_paths:
            final_files.append(ConfFile(f, vc))

    # assemble context
    context = assemble_context()

    # determine VCS usability / defaults merging like original
    vcs_info = determine_vcs_usability()
    context.update(vcs_info)

    # NOTE: Determine new version. If new_version_str is None here,
    #   ``bump_version_by_part_or_literal`` should have raised earlier.
    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, current_version, part, new_version, context
    )

    # NOTE: verify each file contains the current version
    check_files_contain_version(final_files, current_version, context)

    # NOTE: replace in files
    replace_version_in_files(
        final_files, current_version, new_version_str, dry_run, context
    )

    try:
        save_config(
            cfg_path, cfg_format, defaults, new_version_str, dry_run=dry_run
        )
    except Exception as exc:
        logger.info(f"Unable to update config file: {exc}")

    # NOTE: Commit and tag if requested
    selected_vcs = determine_vcs_dirty(allow_dirty=allow_dirty)

    # Build args mapping to satisfy commit_and_tag_if_required
    args_map: dict[str, Any] = {
        "commit": (
            commit if commit is not None else defaults.get("commit", False)
        ),
        "tag": tag if tag is not None else defaults.get("tag", False),
        "sign_tags": (
            sign_tags
            if sign_tags is not None
            else defaults.get("sign_tags", False)
        ),
        "tag_name": tag_name,
        "tag_message": tag_message,
        "message": message,
        "commit_args": commit_args,
    }
    if selected_vcs:
        try:
            commit_and_tag_if_required(
                selected_vcs,
                final_files,
                cfg_path,
                cfg_path is not None,
                args_map,
                current_version,
                new_version_str,
                dry_run,
            )
        except Exception as exc:
            logger.error(f"VCS commit/tag failed: {exc}")
            raise

    # NOTE: print list if requested (old behavior used logger_list).
    #   We'll print key-values if requested.
    if obj.get("show_list"):
        # mimic original config listing style
        kv = defaults.copy()
        kv["new_version"] = new_version_str
        for k, v in kv.items():
            click.echo(f"{k}={v}")

    click.echo(f"Bumped {current_version} → {new_version_str}")
