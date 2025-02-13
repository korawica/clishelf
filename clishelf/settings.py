# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import datetime
import re
from textwrap import dedent


class GitConf:
    """Git config setting data that will use be the baseline data."""

    branch_types: list[str] = ["feature", "bug", "hot"]

    # NOTE: These branch names are not validated with this same rules
    # (permissions should be configured on the server if you want to prevent
    # pushing to any of these):
    branch_excepts: list[str] = [
        "feature",
        "feat",
        "dev",
        "main",
        "stable",
        # NOTE: For quickly fixing critical issues, usually with a temporary
        #   solution.
        "hotfix",
        "bugfix",  # for fixing a bug
        "feature",  # for adding, removing or modifying a feature
        "test",  # for experimenting something which is not an issue
        "wip",  # for a work in progress
    ]

    regex_branch_types: str = "|".join(branch_types)

    regex_commit_msg: str = (
        r"(?P<prefix>\w+)(?:\((?P<topic>\w+)\))?: (?P<header>.+)"
    )

    # TODO: reference emoji from https://gitmoji.dev/
    #   All emojis, https://github.com/ikatyang/emoji-cheat-sheet
    #   GitHub API: https://api.github.com/emojis
    commit_prefix: tuple[tuple[str, str, str]] = (
        # NOTE: Features
        ("feature", "Features", ":dart:"),  # 🎯, 📋 :clipboard:, ✨ :sparkles:
        ("feat", "Features", ":dart:"),  # 🎯, 📋 :clipboard:, ✨ :sparkles:
        ("highlight", "Highlight Features", ":star:"),  # ⭐
        ("hl", "Highlight Features", ":star:"),  # ⭐
        # NOTE: Fixed
        ("hotfix", "Bug fixes", ":fire:"),  # 🔥, 🚑 :ambulance:
        ("fixed", "Bug fixes", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
        ("fix", "Bug fixes", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
        ("bug", "Bug fixes", ":bug:"),  # 🐛
        ("bugfix", "Bug fixes", ":bug:"),  # 🐛
        # NOTE: Documents
        ("docs", "Documents", ":page_facing_up:"),  # 📄, 📑 :bookmark_tabs:
        # NOTE: Code Styled
        ("styled", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
        ("style", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
        (
            "refactored",
            "Code Changes",
            ":construction:",
        ),  # 🚧, 💬 :speech_balloon:
        (
            "refactor",
            "Code Changes",
            ":construction:",
        ),  # 🚧, 💬 :speech_balloon:
        # NOTE: Performance
        (
            "perf",
            "Performance improvements",
            ":zap:",
        ),  # ⚡, 📈 :chart_with_upwards_trend:, ⌛ :hourglass:
        # NOTE: Tests
        ("tests", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
        ("test", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
        ("build", "Build & Workflow", ":toolbox:"),  # 🧰, 📦 :package:
        ("workflow", "Build & Workflow", ":rocket:"),  # 🚀, 🕹️ :joystick:
        ("deps", "Dependencies", ":pushpin:"),  # 📌, 🔍 :mag:
        ("dependency", "Dependencies", ":pushpin:"),  # 📌, 🔍 :mag:
        ("secure", "Security", ":lock:"),  # 🔒
        ("security", "Security", ":lock:"),  # 🔒
        ("init", "Features", ":tada:"),  # 🎉
        ("initial", "Features", ":tada:"),  # 🎉
        ("deprecate", "Deprecate & Clean", ":wastebasket:"),  # 🗑️
        ("clean", "Deprecate & Clean", ":recycle:"),  # ♻️️
        ("drop", "Deprecate & Clean", ":coffin:"),  # ⚰️
        ("revert", "Code Changes", ":rewind:"),  # ⏪
        ("merge", "Code Changes", ":fast_forward:"),  # ⏩
        ("merged", "Code Changes", ":fast_forward:"),  # ⏩
        # NOTE: GitHub custom emoji
        ("dependabot", "Dependencies", ":dependabot:"),
    )

    commit_prefix_group: tuple[tuple[str, str, int]] = (
        ("Highlight Features", ":stars:", 0),  # 🌠
        ("Features", ":sparkles:", 10),  # ✨
        ("Code Changes", ":black_nib:", 30),  # ✒️
        # ("Documents", ":card_file_box:"),  # 🗃️, 📑 :bookmark_tabs:
        ("Documentations", ":book:", 90),  # 📖
        ("Bug fixes", ":bug:", 20),  # 🐛, 🐞:beetle:
        ("Build & Workflow", ":package:", 80),  # 📦
        ("Dependencies", ":postbox:", 80),  # 📮
        ("Security", ":closed_lock_with_key:", 70),  # 🔐
        ("Performance improvements", ":rocket:", 30),  # 🚀, ⚡️ :zap:
        ("Other improvements", ":hammer_and_wrench:", 40),  # 🛠️
        ("Enhancements", ":sparkles:", 40),  # ✨
        ("Deprecate & Clean", ":broom:", 40),  # 🧹, ⛔ :no_entry:
    )

    commit_prefix_emoji_default: str = ":construction:"  # 🚧
    commit_prefix_group_default: str = "Code Changes"
    commit_prefix_group_emoji_default: str = ":black_nib:"  # ✒️

    log_formats: dict[str, str] = {
        "author_name": "%an",
        "author_email": "%ae",
        "author_date": "%ai",
        "hash_full": "%H",
        "hash": "%h",
        "commit_name": "%cn",
        "commit_email": "%ce",
        "commit_date": "%ci",
        "commit_subject": "%s",
        "commit_body": "%b",
        "refs": "%D",
    }

    commit_msg_format: str = "{emoji} {prefix}: {subject}"


class BumpVerConf:
    """Bump Version Config."""

    main: str = dedent(
        r"""
    [bumpversion]
    current_version = {version}
    commit = True
    tag = False
    parse = ^
        {regex}
    serialize =
        {{major}}.{{minor}}.{{patch}}.{{prekind}}{{pre}}.{{postkind}}{{post}}
        {{major}}.{{minor}}.{{patch}}.{{prekind}}{{pre}}
        {{major}}.{{minor}}.{{patch}}.{{postkind}}{{post}}
        {{major}}.{{minor}}.{{patch}}
    message = {msg}

    [bumpversion:part:prekind]
    optional_value = _
    values =
        _
        a
        b
        rc

    [bumpversion:part:postkind]
    optional_value = _
    values =
        _
        post

    [bumpversion:file:{file}]
    """
    ).strip()

    main_dt: str = dedent(
        r"""
    [bumpversion]
    current_version = {version}
    new_version = {new_version}
    commit = True
    tag = False
    parse = ^
        {regex}
    serialize =
        {{date}}.{{pre}}
        {{date}}
    message = {msg}

    [bumpversion:file:{file}]
    """
    )

    msg: str = (
        # 🏷️ :label:, 🔖 :bookmark:
        ":label: Bump up to version {current_version} -> {new_version}."
    )

    regex: str = (
        r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
        r"(\.(?P<prekind>a|alpha|b|beta|d|dev|rc)(?P<pre>\d+))?"
        r"(\.(?P<postkind>post)(?P<post>\d+))?"
    )

    regex_dt: str = r"(?P<date>\d{4}\d{2}\d{2})(\.(?P<pre>\d+))?"

    v1: str = dedent(
        r"""
    {main}

    [bumpversion:file:{changelog}]
    search = {{#}}{{#}} Latest Changes
    replace = {{#}}{{#}} Latest Changes

        {{#}}{{#}} {{new_version}}
    """
    ).strip()

    v2: str = dedent(
        r"""
    {main}

    [bumpversion:file:{changelog}]
    search = {{#}}{{#}} Latest Changes
    replace = {{#}}{{#}} Latest Changes

        {{#}}{{#}} {{new_version}}

        Released: {{utcnow:%Y-%m-%d}}
    """
    ).strip()

    commit_subject_format: str = "{emoji} {prefix}: {subject}"
    commit_msg_format: str = "- {subject} (_{datetime:%Y-%m-%d}_)"

    @classmethod
    def get_version(
        cls,
        version: int,
        params: dict[str, str],
        is_dt: bool = False,
    ) -> str:
        """Generate the `bump2version` config from specific version

        :rtype: str
        """
        if not hasattr(cls, f"v{version}"):
            version = 1
        template: str = getattr(cls, f"v{version}")
        if is_dt:
            if (action := params.get("action", "date")) == "date":
                new_version: str = datetime.datetime.now().strftime("%Y%m%d")
            elif action == "pre":
                new_version = cls.update_dt_pre(params.get("version"))
            else:
                raise ValueError(
                    f"the action does not support for {action} with use "
                    f"datetime mode."
                )
            return template.format(
                changelog=params.get("changelog"),
                main=cls.main_dt.format(
                    version=params.get("version"),
                    new_version=new_version,
                    msg=cls.msg,
                    regex=cls.regex_dt,
                    file=params.get("file"),
                ),
            )
        return template.format(
            changelog=params.get("changelog"),
            main=cls.main.format(
                version=params.get("version"),
                msg=cls.msg,
                regex=cls.regex,
                file=params.get("file"),
            ),
        )

    @classmethod
    def update_dt_pre(cls, version: str) -> str:
        """Return new pre version of datetime mode.

        :param version: A string version that want to update.

        Examples:
            20240101        ->  20240101.1
            20240101.2      ->  20240101.3
            20240101.post   ->  20240101.1

        :rtype: str
        """
        if search := re.search(BumpVerConf.regex_dt, version):
            search_dict: dict[str, str] = search.groupdict()
            if pre := search_dict.get("pre"):
                pre = str(int(pre) + 1)
            else:
                pre = "1"
            return f"{search_dict['date']}.{pre}"
        raise ValueError(
            "version value does not match with datetime regex string."
        )

    @classmethod
    def get_regex(cls, is_dt: bool = False) -> str:
        """Get the regular expression format string.

        :rtype: str
        """
        return cls.regex_dt if is_dt else cls.regex
