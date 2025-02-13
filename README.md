# CLI on the Shelf

[![test](https://github.com/korawica/clishelf/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/clishelf/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/korawica/clishelf/graph/badge.svg?token=7PF8JN2EIG)](https://codecov.io/gh/korawica/clishelf)
[![pypi version](https://img.shields.io/pypi/v/clishelf)](https://pypi.org/project/clishelf/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clishelf?logo=pypi)](https://pypi.org/project/clishelf/)
[![size](https://img.shields.io/github/languages/code-size/korawica/clishelf)](https://github.com/korawica/clishelf)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![gh license](https://img.shields.io/github/license/ddeutils/ddeutil-observe)](https://github.com/ddeutils/ddeutil-workflow/blob/main/LICENSE)

A CLI tools and hooks on my shelf for my any Python packages.
This project help me to make Versioning, run Abbreviate of Git CLI.

> [!NOTE]
> This project was created because I do not want to hard code set up all of them
> every time when I start create a new Python package :tired_face:. I provide some
> reusable CLIs that was implemented by [`Click`](https://github.com/pallets/click/).

## :round_pushpin: Installation

```shell
pip install -U clishelf
```

In the future, I will add more the CLI tools that able to dynamic with
many style of config such as I want to make changelog file with style B by my
custom message code.

**Dependency supported**:

| Python Version   | Installation                       |  Support Fixed Bug   |
|:-----------------|:-----------------------------------|:--------------------:|
| `== 3.8`         | `pip install "clishelf<=0.1.10"`   |         :x:          |
| `>=3.9.13,<3.14` | `pip install -U clishelf`          |  :heavy_check_mark:  |

> [!WARNING]
> This package already install `pre-commit` with the latest version.

## :rocket: Pre-Commit Hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

```yaml
- repo: https://github.com/korawica/clishelf
  rev: v0.2.19
  hooks:
    - id: shelf-commit-msg
      stages: [commit-msg]
```

## :tada: Features

This Utility Package provide some CLI tools for handler development process.

```text
Usage: shelf.exe [OPTIONS] COMMAND [ARGS]...

  The Main Shelf commands.

Commands:
  conf   Return config for clishelf commands
  cove   Run the coverage command.
  dep    List of Dependencies that was set in pyproject.toml file.
  emoji  The Emoji commands
  git    The Extended Git commands
  vs     The Versioning commands.
```

### Extended Git

This is abbreviation of Git CLI that warped with the Python subprocess package.

```text
Usage: shelf.exe git [OPTIONS] COMMAND [ARGS]...

  The Extended Git commands

Commands:
  bn-clear     Clear Local Branches that sync from the Remote repository.
  cm           Prepare and show the latest commit message with the commit...
  cm-prev      Commit changes to the Previous Commit with same message.
  cm-revert    Revert the latest Commit on the Local repository.
  mg           Merge change from another branch with strategy, `theirs`...
  tg-clear     Clear Local Tags that sync from the Remote repository.
```

### Versioning

This is the enhancement `bump2version` Python package for my bumping style.

```text
Usage: shelf.exe vs [OPTIONS] COMMAND [ARGS]...

  The Versioning commands.

Commands:
  bump       Bump package version with a next tag value with an input...
  changelog  Make a changelog file that generate form previous commits.
  current    Return Current Version that read from ``__about__`` by default.
```

### Emoji

This is the emoji CLI that getting data from GitHub dataset.

```text
Usage: shelf.exe emoji [OPTIONS] COMMAND [ARGS]...

  The Emoji commands

Commands:
  fetch  Refresh emoji metadata file on assets folder.
```

## :cookie: Configuration

### Basic Setting

`.clishelf.yaml`:

```yaml
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

### Override Commit Prefix

```yaml
git:
  commit_prefix:
    - ["comment", "Documents", ":bulb:"]  # 💡
    - ["typos", "Documents", ":pencil2:"]  # ✏️
  commit_prefix_group:
    - ["Features", ":tada:"]  # 🎉
```

| Module   | Key                        | Default                                 | Description                                                                                         |
|:---------|:---------------------------|:----------------------------------------|:----------------------------------------------------------------------------------------------------|
| git      | commit_prefix              | `None`                                  | Commit prefix that want to override/append                                                          |
|          | commit_prefix_group        | `None`                                  | Commit prefix group that want to override/append                                                    |
|          | commit_msg_format          | `"{emoji} {prefix}: {subject}"`         | Commit message format that use to prepare                                                           |
|          | commit_prefix_pre_demojize | `True`                                  | Auto de-emoji on a commit log subject                                                               |
|          | commit_prefix_force_fix    | `False`                                 | Force fix if commit message does not match with normal form                                         |
| version  | version                    | `"./{PROJECT-NAME}/__about__.py"`       | Version tracking file location path (with `.py` format)                                             |
|          | changelog                  | `"CHANGELOG.md"`                        | Changelog file location path                                                                        |
|          | mode                       | `"normal"`                              | `"normal"` for normal version<br>`"datetime"` for datetime time mode (format `%Y%m%d.%pre-release`) |
|          | commit_subject_format      | `"{emoji} {prefix}: {subject}"`         | Commit subject format that use to writing a changelog file with `commit_msg_format`                 |
|          | commit_msg_format          | `"- {subject} (_{datetime:%Y-%m-%d}_)"` | Commit message format that use to writing a changelog file                                          |

## :dart: Mini-Roadmap

- (**Optional**) I will implement use `rich` and `alive-progress` to this project for make
  interface terminal prettier.
- (**Optional**) Dynamic emoji changing for support other platform such as GitLab.
- (**BIG**) Remove `bump2version` package and implement my bump function instead.

> [!NOTE]
> I will migrate this code from **Python** to **Rust** for performance of this CLI
> (But I will observe for this again because this package does not have any issue with perf as well).

## :speech_balloon: Contribute

I do not think this project will go around the world because it has specific propose,
and you can create by your coding without this project dependency for long term
solution. So, on this time, you can open [the GitHub issue on this project :raised_hands:](https://github.com/korawica/clishelf/issues)
for fix bug or request new feature if you want it.
