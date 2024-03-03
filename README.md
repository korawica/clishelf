# Utility Package: *CLI Shelf*

[![test](https://github.com/korawica/clishelf/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/clishelf/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/korawica/clishelf/graph/badge.svg?token=7PF8JN2EIG)](https://codecov.io/gh/korawica/clishelf)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clishelf?logo=pypi)](https://pypi.org/project/clishelf/)
[![size](https://img.shields.io/github/languages/code-size/korawica/clishelf)](https://github.com/korawica/clishelf)

**Table of Contents**:

* [Installation](#installation)
* [Pre-Commit Hook](#pre-commit-hook)
* [Features](#features)
  * [Extended Git](#extended-git)
  * [Versioning](#versioning)
  * [Emoji](#emoji)
* [Configuration](#configuration)

This is the **Utility CLI Tools and Hooks on the Shelf** for my Python packages
that help me to make Versioning, Abbreviate of Git CLI, and Wrapped Dev Python packages
(`coverage`, `pre-commit`) on my any Python package repositories.

This project was created because I do not want to hard code set up all of them
every time when I start create a new Python package :tired_face:. I provide some
reusable CLIs that was implemented from the [`Click`](https://github.com/pallets/click/)
package.

## Installation

```shell
pip install clishelf
```

In the future, I will add more the CLI tools that able to dynamic with
many style of config such as I want to make changelog file with style B by my
custom message code.

**Dependency supported**:

| Python Version   | Installation                            |
|------------------|-----------------------------------------|
| `== 3.8`         | `pip install "clishelf>=0.1.10,<0.2.0"` |
| `>=3.9.13,<3.13` | `pip install -U clishelf`               |

## Pre-Commit Hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

```yaml
- repo: https://github.com/korawica/clishelf
  rev: v0.2.0
  hooks:
    - id: shelf-commit-msg
      stages: [commit-msg]
```

## Features

This Utility Package provide some CLI tools for handler development process.

```text
Usage: shelf.exe [OPTIONS] COMMAND [ARGS]...

  The Main Shelf commands.

Options:
  --help  Show this message and exit.

Commands:
  conf   Return config for clishelf commands
  cove   Run the coverage command.
  dep    List of Dependencies that was set in pyproject.toml file.
  echo   Echo Hello World
  emoji  The Emoji commands
  git    The Extended Git commands
  vs     The Versioning commands.
```

**List of Features**:

* [Extended Git](#extended-git)
* [Versioning](#versioning)
* [Emoji](#emoji)

### Extended Git

This is abbreviation of Git CLI that warped with the Python subprocess package.

```text
Usage: shelf.exe git [OPTIONS] COMMAND [ARGS]...

  The Extended Git commands

Options:
  --help  Show this message and exit.

Commands:
  bn           Show the Current Branch name.
  bn-clear     Clear Local Branches that sync from the Remote repository.
  cm           Show the latest Commit message
  cm-prev      Commit changes to the Previous Commit with same message.
  cm-revert    Revert the latest Commit on the Local repository.
  df           Show changed files from previous commit to HEAD
  init         Initialize GIT config on local
  log          Show the Commit Logs from the latest Tag to HEAD.
  mg           Merge change from another branch with strategy, `theirs`...
  pf           Show Profile object that contain Name and Email of Author
  tg           Show the Latest Tag if it exists, otherwise it will show...
  tg-clear     Clear Local Tags that sync from the Remote repository.
```

### Versioning

This is the enhancement `bump2version` Python package for my bumping style.

```text
Usage: shelf.exe vs [OPTIONS] COMMAND [ARGS]...

  The Versioning commands.

Options:
  --help  Show this message and exit.

Commands:
  bump       Bump Version with specific action.
  changelog  Make Changelogs file
  conf       Return the config data for bumping version.
  current    Return Current Version that read from ``__about__`` by default.
  tag        Create the Git tag by version from the ``__about__`` file.
```

### Emoji

This is the emoji CLI that getting data from GitHub dataset.

```text
Usage: shelf.exe emoji [OPTIONS] COMMAND [ARGS]...

  The Emoji commands

Options:
  --help  Show this message and exit.

Commands:
  fetch  Refresh emoji metadata file on assets folder.
  ls     List all emojis from metadata file.
```

## Configuration

The configuration able to be `.clishelf.yaml` or mapping value in `pyproject.toml`.

`.clishelf.yaml`:

```yaml
git:
  commit_prefix:
    - ["comment", "Documents", ":bulb:"]  # 💡
    - ["typos", "Documents", ":pencil2:"]  # ✏️
  commit_prefix_group:
    - ["Features", ":tada:"]  # 🎉
version:
  version: "./clishelf/__about__.py"
  changelog: "CHANGELOG.md"
  mode: "normal"
```

`pyproject.toml`:

```toml
[tool.shelf.version]
version = "./clishelf/__about__.py"
changelog = "CHANGELOG.md"
mode = "normal"
```

> [!IMPORTANT]
> The bump version mode able to be `normal` or `datetime` only.

## License

This project was licensed under the terms of the [MIT license](LICENSE).
