from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from ..errors import (
    IncompleteVersionRepresentationException,
    MissingValueForSerializationException,
    WorkingDirectoryIsDirtyException,
)
from .utils import ConfFile, kv_str, prefixed_env
from .vcs import Git, Mercurial
from .version_part import Version, VersionConfig

logger = logging.getLogger(__name__)
time_context: dict[str, datetime] = {
    "now": datetime.now(),
    "utcnow": datetime.now(timezone.utc),
}
special_char_context: dict[str, str] = {"#": "#", ";": ";"}
VCS_HANDLERS = [Git, Mercurial]


def determine_vcs_usability() -> dict[str, Any]:
    """Determine usable VCS and return latest tag info merged.

    This mirrors the original behavior: check each VCS.is_usable and gather
    latest_tag_info.
    """
    vcs_info: dict[str, Any] = {}
    for vcs in VCS_HANDLERS:
        if vcs.is_usable():
            vcs_info.update(vcs.latest_tag_info())
    return vcs_info


def determine_vcs_dirty(allow_dirty: bool = False):
    """
    Return the first usable VCS class that is not dirty (unless allow_dirty).
    Mirrors original `_determine_vcs_dirty`.
    """
    for vcs in VCS_HANDLERS:
        if not vcs.is_usable():
            continue
        try:
            vcs.assert_nondirty()
        except WorkingDirectoryIsDirtyException as e:
            if not allow_dirty:
                logger.warning(
                    f"{e}\n\nUse --allow-dirty to override this if you know what you're doing."
                )
                raise
        return vcs
    return None


def assemble_context(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx: dict[str, Any] = {**time_context, **prefixed_env()}
    if extra:
        ctx.update(extra)
    ctx.update(special_char_context)
    return ctx


def opportunistic_bump_part_and_serialize(
    part: str,
    current_version_obj: Version,
    version_config: VersionConfig,
    context: dict[str, Any],
) -> str | None:
    """Attempt to increment the indicated part and serialize — returns
    serialized string.

    Mirrors `_assemble_new_version` opportunistic part bumping when new_version
    is implied.
    """
    try:
        new_version_obj = current_version_obj.bump(part, version_config.order())
        logger.info(f"Values are now: {kv_str(new_version_obj.values)}")
        return version_config.serialize(new_version_obj, context)
    except (
        MissingValueForSerializationException,
        IncompleteVersionRepresentationException,
    ) as e:
        logger.info(f"Opportunistic finding of new_version failed: {e}")
    except KeyError:
        logger.info("Opportunistic finding of new_version failed")
    return None


def bump_version_by_part_or_literal(
    version_config: VersionConfig,
    current_version_str: str,
    part: str | None,
    explicit_new_version_str: str | None,
    context: dict[str, Any],
) -> tuple[Version | None, Version | None, str]:
    """Determine the new version either by:
      - explicit_new_version_str (parsing via version_config)
      - or, if part provided, increment that part on the parsed current_version.

    Returns (old_version_obj, new_version_obj, new_version_str)
    """
    current_obj = version_config.parse(current_version_str)

    if explicit_new_version_str:
        new_obj = version_config.parse(explicit_new_version_str)
        new_str = explicit_new_version_str
    else:
        if not part:
            raise ValueError(
                "No part specified and no explicit new version provided"
            )
        new_str: str | None = opportunistic_bump_part_and_serialize(
            part, current_obj, version_config, context
        )
        if new_str is None:
            # last resort: perform bump on object and serialize
            new_obj = current_obj.bump(part, version_config.order())
            new_str = version_config.serialize(new_obj, context)
        else:
            new_obj = version_config.parse(new_str)
    return current_obj, new_obj, new_str


def check_files_contain_version(
    files: Iterable[ConfFile],
    current_version_str: str,
    context: dict[str, Any],
):
    for f in files:
        f.should_contain_version(current_version_str, context)


def replace_version_in_files(
    files: Iterable[ConfFile],
    current_version,
    new_version,
    dry_run: bool,
    context: dict[str, Any],
):
    for f in files:
        f.replace(current_version, new_version, context, dry_run)


def commit_and_tag_if_required(
    vcs,
    files,
    config_file,
    config_file_exists: bool,
    args: dict[str, Any],
    current_version_str: str,
    new_version_str: str,
    dry_run: bool,
):
    """
    Commit updated files and tag using vcs class. `vcs` is a VCS class.
    This mirrors `_commit_to_vcs` and `_tag_in_vcs`.
    """
    commit_files = [f.path for f in files]
    if config_file_exists and config_file:
        commit_files.append(str(config_file))

    if not vcs or not vcs.is_usable():
        raise AssertionError(
            f"Did find '{vcs.__name__}' unusable, unable to commit."
        )

    do_commit: bool = args.get("commit", False) and not dry_run
    print(
        f'{"Would prepare" if not do_commit else "Preparing"} '
        f"{vcs.__name__} commit"
    )
    for path in commit_files:
        print(
            f'{"Would add" if not do_commit else "Adding"} changes in file '
            f"{path!r} to {vcs.__name__}"
        )
        if do_commit:
            vcs.add_path(path)

    context: dict[str, Any] = {
        "current_version": current_version_str,
        "new_version": new_version_str,
    }
    context.update(time_context)
    context.update(prefixed_env())
    # add parts into context if available
    try:
        # current and new are parseable into dict-like objects
        context.update({"current_" + part: current_version_str for part in []})
    except Exception:
        pass

    commit_message = args.get(
        "message", "Bump version: {current_version} → {new_version}"
    ).format(**context)
    logger.info(
        "%s to %s with message '%s'",
        "Would commit" if not do_commit else "Committing",
        vcs.__name__,
        commit_message,
    )
    if do_commit:
        vcs.commit(
            message=commit_message,
            context=context,
            extra_args=[
                arg.strip()
                for arg in args.get("commit_args", "").splitlines()
                if arg.strip()
            ],
        )

    # tagging
    sign_tags = args.get("sign_tags", False)
    tag_name = args.get("tag_name", "v{new_version}").format(**context)
    tag_message = args.get(
        "tag_message", "Bump version: {current_version} → {new_version}"
    ).format(**context)
    do_tag = args.get("tag", False) and not dry_run
    logger.info(
        "%s '%s' %s in %s and %s",
        "Would tag" if not do_tag else "Tagging",
        tag_name,
        f"with message '{tag_message}'" if tag_message else "without message",
        vcs.__name__,
        "signing" if sign_tags else "not signing",
    )
    print(f"Start do tag or not: {do_tag}")
    if do_tag:
        vcs.tag(sign_tags, tag_name, tag_message)
