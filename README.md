# Utility Package: *CLI Shelf*

[![test](https://github.com/korawica/clishelf/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/clishelf/actions/workflows/tests.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clishelf?logo=pypi)](https://pypi.org/project/clishelf/)
[![size](https://img.shields.io/github/languages/code-size/korawica/clishelf)](https://github.com/korawica/clishelf)

**Table of Contents**:

- [Installation](#installation)
- [Features](#features)
  - [Extended Git](#extended-git)
  - [Versioning](#versioning)

This is the **CLI Utility** Python package for help me to make versioning and
logging on my any Python package repositories, because I do not want to hard
code or set up the development flow every time that I create the new Python
package project :tired_face:.

## Installation

```shell
pip install clishelf
```

In the future, I will add more the CLI tools that able to dynamic with
many style of config such as I want to make changelog file with style B by my
custom message code.

## Features

This Utility Package provide some CLI tools for handler development process.

```text
Usage: shelf.exe [OPTIONS] COMMAND [ARGS]...

  A simple command line tool.

Options:
  --help  Show this message and exit.

Commands:
  cove  Run Coverage flow
  echo  Echo Hello World
  git   Extended Git commands
  vs    Versioning commands
```

### Extended Git

```text
Usage: shelf.exe git [OPTIONS] COMMAND [ARGS]...

  Extended Git commands

Options:
  --help  Show this message and exit.

Commands:
  bn               Show the Current Branch name.
  cl               Show the Commit Logs from the latest Tag to HEAD.
  clear-branch     Clear Local Branches that sync from the Remote...
  clear-tag        Clear Local Tags that sync from the Remote repository.
  cm               Show the latest Commit message
  commit-previous  Commit changes to the Previous Commit with same message.
  commit-revert    Revert the latest Commit on the Local repository.
  init-conf        Initialize GIT config on local
  profile          Show Profile object that contain Name and Email of Author
  tl               Show the Latest Tag if it exists, otherwise it will...
```

### Versioning

```text
Usage: shelf.exe vs [OPTIONS] COMMAND [ARGS]...

  Versioning commands

Options:
  --help  Show this message and exit.

Commands:
  bump       Bump Version
  changelog  Make Changelogs file
  conf       Return Configuration for Bump version
  current    Return Current Version
  tag        Create the Git tag from the about file.
```

## License

This project was licensed under the terms of the [MIT license](LICENSE).
