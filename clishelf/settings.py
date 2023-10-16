# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from textwrap import dedent
from typing import List


class GitConf:
    branch_types: List[str] = ["feature", "bug", "hot"]
    regex_branch_types: str = "|".join(branch_types)


class BumpVerConf:
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

    msg: str = (
        ":bookmark: Bump up to version {{current_version}} -> {{new_version}}."
    )

    regex: str = (
        r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
        r"(\.(?P<prekind>a|alpha|b|beta|d|dev|rc)(?P<pre>\d+))?"
        r"(\.(?P<postkind>post)(?P<post>\d+))?"
    )

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
