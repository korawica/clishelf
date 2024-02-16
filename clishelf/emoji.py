# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
import json
from datetime import datetime
from pathlib import Path

import click
import requests

cli_emoji: click.Command


# Dataset: https://github.com/github/gemoji/blob/master/db/emoji.json
GH_EMOJI_URL: str = (
    "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"
)


def get_emojis():
    file = Path(__file__).parent / "assets/emoji.json"
    with file.open(encoding="utf-8") as f:
        yield from iter(json.load(f))


def demojize(msg: str):
    for emojis in get_emojis():
        if (emoji := emojis["emoji"]) in msg:
            msg = msg.replace(emoji, f':{emojis["alias"]}:')
    return msg


def emojize(msg: str):
    for emojis in get_emojis():
        if (alias := f':{emojis["alias"]}:') in msg:
            msg = msg.replace(alias, emojis["emoji"])
    return msg


@click.group(name="emoji")
def cli_emoji():
    """The Emoji commands"""
    pass  # pragma: no cover.


@cli_emoji.command()
@click.option("-b", "--backup", is_flag=True)
def fetch(backup: bool):
    """Refresh emoji metadata file on assets folder."""
    file = Path(__file__).parent / "assets/emoji.json"
    file.parent.mkdir(exist_ok=True)
    if file.exists() and backup:
        file.rename(file.parent / f"emoji.bk{datetime.now():%Y%m%d%H%M%S}.json")
    with file.open(mode="w", encoding="utf-8") as f:
        prepare = [
            {"emoji": data["emoji"], "alias": data["aliases"][0]}
            for data in requests.get(GH_EMOJI_URL).json()
        ]
        json.dump(prepare, f, indent=2)


@cli_emoji.command()
def ls():
    """List all emojis from metadata file."""
    for info in get_emojis():
        click.echo(info)


if __name__ == "__main__":
    cli_emoji.main()
