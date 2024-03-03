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
    """Git Config."""

    branch_types: list[str] = ["feature", "bug", "hot"]

    # These branch names are not validated with this same rules
    # (permissions should be configured on the server if you want to prevent
    # pushing to any of these):
    branch_excepts: list[str] = [
        "feature",
        "dev",
        "main",
        "stable",
        # for quickly fixing critical issues, usually with a temporary solution.
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
        ("feature", "Features", ":dart:"),  # 🎯, 📋 :clipboard:, ✨ :sparkles:
        ("feat", "Features", ":dart:"),  # 🎯, 📋 :clipboard:, ✨ :sparkles:
        ("hotfix", "Fix Bugs", ":fire:"),  # 🔥, 🚑 :ambulance:
        ("fixed", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
        ("fix", "Fix Bugs", ":gear:"),  # ⚙️, 🛠️ :hammer_and_wrench:
        ("bug", "Fix Bugs", ":bug:"),  # 🐛
        ("docs", "Documents", ":page_facing_up:"),  # 📄, 📑 :bookmark_tabs:
        ("styled", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
        ("style", "Code Changes", ":art:"),  # 🎨, 📝 :memo:, ✒️ :black_nib:
        ("refactored", "Code Changes", ":construction:"),
        # 🚧, 💬 :speech_balloon:
        ("refactor", "Code Changes", ":construction:"),
        # 🚧, 💬 :speech_balloon:
        ("perf", "Code Changes", ":zap:"),
        # ⚡, 📈 :chart_with_upwards_trend:, ⌛ :hourglass:
        ("tests", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
        ("test", "Code Changes", ":test_tube:"),  # 🧪, ⚗️ :alembic:
        ("build", "Build & Workflow", ":toolbox:"),  # 🧰, 📦 :package:
        ("workflow", "Build & Workflow", ":rocket:"),  # 🚀, 🕹️ :joystick:
        ("deps", "Dependencies", ":pushpin:"),  # 📌, 🔍 :mag:
        ("dependency", "Dependencies", ":pushpin:"),  # 📌, 🔍 :mag:
        ("secure", "Security", ":lock:"),  # 🔒
        ("init", "Features", ":tada:"),  # 🎉
        ("deprecate", "Code Changes", ":wastebasket:"),  # 🗑️
        ("revert", "Code Changes", ":rewind:"),  # ⏪
    )

    commit_prefix_group: tuple[tuple[str, str]] = (
        ("Features", ":sparkles:"),  # ✨
        ("Code Changes", ":black_nib:"),  # ✒️
        ("Documents", ":card_file_box:"),  # 🗃️, 📑 :bookmark_tabs:
        ("Fix Bugs", ":bug:"),  # 🐛
        ("Build & Workflow", ":package:"),  # 📦
        ("Dependencies", ":postbox:"),  # 📮
        ("Security", ":closed_lock_with_key:"),  # 🔐
    )


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
    # main_dt: str = dedent(
    #     r"""
    # [bumpversion]
    # current_version = {version}
    # new_version = {new_version}
    # commit = True
    # tag = False
    # parse = ^
    #     {regex}
    # serialize =
    #     {{date}}.{{pre}}
    #     {{date}}
    # message = {msg}
    #
    # [bumpversion:file:{file}]
    # """
    # )

    msg: str = (
        # 🔖 :bookmark:
        ":bookmark: Bump up to version {current_version} -> {new_version}."
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

    @classmethod
    def get_version(
        cls,
        version: int,
        params: dict[str, str],
        is_dt: bool = False,
    ):
        """Generate the `bump2version` config from specific version"""
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
    def update_dt_pre(cls, version: str):
        """Return new pre version of datetime mode.
        Examples:
            20240101        ->  20240101.1
            20240101.2      ->  20240101.3
            20240101.post   ->  20240101.1
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
        return cls.regex_dt if is_dt else cls.regex
