# Utility Package: *CLI*

[![test](https://github.com/korawica/clishelf/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/clishelf/actions/workflows/tests.yml)
[![python support version](https://img.shields.io/pypi/pyversions/clishelf)](https://pypi.org/project/clishelf/)
[![size](https://img.shields.io/github/languages/code-size/korawica/clishelf)](https://github.com/korawica/clishelf)

**Table of Contents**:

- [Feature](#feature)
  - [Extended Git](#extended-git)
  - [Version](#version)

This is CLI Utility Package.

## Feature

This Utility Package provide some CLI tools for handler development process.

### Extended Git

```text
Usage: utils.exe git [OPTIONS] COMMAND [ARGS]...

  Extended Git commands

Options:
  --help  Show this message and exit.

Commands:
  bn               Show the Current Branch
  cl               Show the Commit Logs from the latest Tag to HEAD
  clear-branch     Clear Local Branches that sync from the Remote
  cm               Show the latest Commit message
  commit-previous  Commit changes to the Previous Commit with same message
  commit-revert    Revert the latest Commit on this Local
  tl               Show the Latest Tag
```

### Version

```text
Usage: utils.exe vs [OPTIONS] COMMAND [ARGS]...

  Version commands

Options:
  --help  Show this message and exit.

Commands:
  bump       Bump Version
  changelog  Make Changelogs file
  conf       Return Configuration for Bump version
  current    Return Current Version

```

## License

This project was licensed under the terms of the [MIT license](LICENSE).
