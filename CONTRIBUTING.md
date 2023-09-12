# Contributing

This is the contributing note for me or other people that want to change
and update the code in this repository. I'm not that good at memorizing.
So I created this note to prevent myself from forgetting when coming back
to develop this code.

**Table of Contents**:

- [Getting Started](#getting-started)
- [Develop Feature](#develop-feature)
- [Release Code](#release-code)
  - [Make Versioning](#make-versioning)
  - [Test Installation](#test-pypi-installation)

## Getting Started

First, I will clone the code from my repository or the fork of this repository
to local. Please check the Python version on your local environment that match
with the base version of this package.

```shell
git clone https://github.com/korawica/clishelf.git
```

> **Note**: \
> If you want to set new user and email before push your edited code, you should
> follow below command:
> ```shell
> git config --local user.name "Korawich Anuttra"
> git config --local user.email "korawich.anu@gmail.com"
> git config --local credential.helper ""
> ```
> In accident case, If you commit with the wrong user and email completely, you
> can fix this action by follow below command:
> ```shell
> git commit --amend --no-edit \
>   --author="Korawich Anuttra <korawich.anu@gmail.com>"
> ```

> Warning: \
> If you want to store your credential, you can set git config by
> ```shell
> git config credential.helper store
> ```

Second, I will create the local Python environment by build-in package, `venv`.

```shell
python -m pip install --upgrade pip
python -m venv venv
./env/Scripts/activate
```

> **Note**: \
> For create performance, you can use `virtualenv` instead of build-in `venv`.

Third, I will install this package dependencies on my local environment.

```shell
(venv) $ pip install -e . --no-cache
```

Finally, I will set up the test and development packages for helping me when I
develop this code.

- Pre-Commit Installation

  ```shell
  pre-commit install
  ```

## Develop Feature

This repository have the versioning branching strategy. If I want to add new feature
to the versioning branch, in the below example be `0.0.3` branch, I will create the
feature branch from that branch first.

```shell
git checkout 0.0.3
git checkout -b features/{name-of-feature} 0.0.3
git push origin features/{name-of-feature}
```

If I finish my code develop, I will pull request to my parent versioning branch.

> **Note**: \
> If you have `hotfix` or some little change of the versioning code, you can directly
> develop on your versioning branch and then push the code with the commit format.

## Release Code

### Make Versioning

When you finish the release coding in the versioning branch, you can pull request
the code to the main branch.

```shell
git checkout 0.0.3 ; git pull origin 0.0.3
```

Bump the next patch version from `0.0.2` to `0.0.3`.

```shell
shelf vs bump patch --ignore-changelog
```

Finally, you create the changelog information and edit if it has some detail that you want to add.

```shell
shelf vs changelog ; shelf git commit-previous
```

> **Note**: \
> If it has some accident, you can restore all the change by `git restore .` command.

### Test PyPI Installation

```shell
(venv) $ pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --no-cache \
  "shelf"
(venv) $ pytest -v
```

```shell
(venv) $ git add . ; git commit --amend --no-edit
```
