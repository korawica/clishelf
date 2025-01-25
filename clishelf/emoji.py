# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import click

try:
    import requests
except ImportError:  # pragma: no cov
    requests = None

from .__types import DictStr

cli_emoji: click.Command


# NOTE:
#   The Emoji dataset that provide by GitHub.
#   (refs: https://github.com/github/gemoji/blob/master/db/emoji.json)
GH_EMOJI_URL: str = (
    "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"
)


def get_emojis() -> Iterator[DictStr]:
    """Get the iterator of the emoji data that already loading to assets path.
    This function use iterator for returning step because I do not want to keep
    all emoji data in memory.

    :rtype: Iterator[DictStr]
    """
    file = Path(__file__).parent / "assets/emoji.json"
    with file.open(encoding="utf-8") as f:
        yield from iter(json.load(f))


def demojize(
    msg: str,
    *,
    emojis: Optional[Union[Iterator[DictStr], list[DictStr]]] = None,
) -> str:
    """Replace a Unicode emoji to an emoji string in a message.

    :param msg: A message string that want to search emoji string.
    :param emojis: An iterator or list of mapping of emoji values.

    :rtype: str
    """
    emojis: Iterator[DictStr] = get_emojis() if emojis is None else emojis
    for emoji in emojis:
        if (e := emoji["emoji"]) in msg:
            msg = msg.replace(e, f':{emoji["alias"]}:')
    return msg


def emojize(
    msg: str,
    *,
    emojis: Optional[Union[Iterator[DictStr], list[DictStr]]] = None,
) -> str:
    """Replace an emoji string to a Unicode emoji in a message.

    :param msg: A message string that want to search Unicode emoji.
    :param emojis: An iterator or list of mapping of emoji values.

    :rtype: str
    """
    emojis: Iterator[DictStr] = get_emojis() if emojis is None else emojis
    for emoji in emojis:
        if (alias := f':{emoji["alias"]}:') in msg:
            msg = msg.replace(alias, emoji["emoji"])
    return msg


@click.group(name="emoji")
def cli_emoji():
    """The Emoji commands"""
    pass  # pragma: no cov


@cli_emoji.command()
@click.option("-b", "--backup", is_flag=True)
def fetch(backup: bool = False) -> None:
    """Refresh emoji metadata file on the assets folder, `./asserts`.

    :param backup: A backup flag for rename the previous file with backup suffix
        if this value set to True.
    :type backup: bool (=False)
    """
    if requests is None:  # pragma: no cov
        raise ImportError(
            "fetch command want the request package for getting the emoji "
            "metadata from the GitHub repository. Please install with: "
            "`pip install -U requests`"
        )

    file: Path = Path(__file__).parent / "assets/emoji.json"
    file.parent.mkdir(parents=True, exist_ok=True)

    if file.exists() and backup:
        file.rename(file.parent / f"emoji.bk{datetime.now():%Y%m%d%H%M%S}.json")

    with file.open(mode="w", encoding="utf-8") as f:
        json.dump(
            [
                {"emoji": data["emoji"], "alias": data["aliases"][0]}
                for data in requests.get(GH_EMOJI_URL).json()
            ],
            f,
            indent=2,
        )


if __name__ == "__main__":
    cli_emoji.main()
