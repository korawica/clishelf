# Changelogs

## Latest Changes

## 0.2.22

### :bug: Bug fixes

- :hammer_and_wrench: fixed: commit message does not support for code block (#143)

### :black_nib: Code Changes

- :twisted_rightwards_arrows: merge: branch 'main' of https://github.com/korawica/clishelf

### :tada: Features

- :dart: feat: add support initial message from gh. (#144)
- :dart: feat: add cli to display all commit prefix values that able to use (#142).
- :dart: feat: add cli to display all commit prefix values that able to use (#142)

## 0.2.21

### :tada: Features

- :dart: feat: add gitmoji style. (#135)

## 0.2.20

### :bug: Bug fixes

- :gear: fixed: revise get dep command logic. (#131)

### :black_nib: Code Changes

- :art: styled: add emoji on bump version message.

### :book: Documents

- :page_facing_up: docs: update readme file.

## 0.2.19

### :bug: Bug fixes

- :gear: fixed: change default priority commit prefix group from 80 to 60.

### :black_nib: Code Changes

- :art: styled: add info level on bump command.

### :book: Documents

- :page_facing_up: docs: update license on pyproject.

### :package: Build & Workflow

- :toolbox: build: add workflow dispatch trigger.

### :postbox: Dependencies

- :pushpin: deps: add PyYAML==6.0.2 on require deps.

## 0.2.18

### :postbox: Dependencies

- :pushpin: deps: move unnecessary deps to optional.

### :tada: Features

- :dart: feat: add more commit prefix.
- :dart: feat: priority commit group before writing the changelog file (#127)

## 0.2.17

### :book: Documents

- :page_facing_up: docs: update readme file.

### :black_nib: Code Changes

- :test_tube: tests: add auto use flag on make conf fixture.

### :bug: Bug fixes

- :bug: fixed: bug merge prefix does not support for generate changelog process (#125)
- :gear: fixed: move version config from yaml file to pyproject.

## 0.2.16

### :package: Build & Workflow

- :toolbox: build: update config of clishelf. (_2025-01-30_)
- :toolbox: build: remove token on publish workflow. (_2025-01-30_)

## 0.2.15.post1

### :package: Build & Workflow

- :toolbox: build: add repo url for testpypi registry. (_2025-01-29_)

## 0.2.15.post0

### :package: Build & Workflow

- :toolbox: build: move using secrets to open id auth. (_2025-01-29_)

## 0.2.15

### :bug: Bug fixes

- :bug: hotfix: commit msg format force change on pre commit message process (#121) (_2025-01-29_)

### :postbox: Dependencies

- :toolbox: deps: update prefix on dependabot. (#119) (_2025-01-28_)

## 0.2.14

### :tada: Features

- :dart: feat: add commit_msg_format config on git mod. (_2025-01-28_)

### :book: Documents

- :page_facing_up: docs: update description on config topic. (_2025-01-28_)
- :page_facing_up: docs: change default value on config. (_2025-01-28_)
- :page_facing_up: docs: update readme file. (_2025-01-28_)

## 0.2.13

### :black_nib: Code Changes

- :test_tube: tests: update make config file if it run in tests path. (_2025-01-28_)
- :arrow_up: refactored: bump pypa/gh-action-pypi-publish from 1.12.3 to 1.12.4 (#117) (_2025-01-27_)

## 0.2.12

### :tada: Features

- :dart: feat: add commit subject data class. (_2025-01-27_)
- :dart: feat: add log format on git setting. (_2025-01-27_)

### :book: Documents

- :page_facing_up: docs: update contributor docs. (_2025-01-27_)

### :black_nib: Code Changes

- :art: styled: change code format. (_2025-01-27_)

### :bug: Bug fixes

- :gear: fixed: date format on git log should iso8601. (_2025-01-27_)

### :package: Build & Workflow

- :toolbox: build: change prefix syntax from ascii to emoji char. (_2025-01-27_)

## 0.2.11

### :black_nib: Code Changes

- :test_tube: tests: update conftest for test path. (_2025-01-26_)
- :art: styled: change code style and code format. (_2025-01-25_)

### :package: Build & Workflow

- :toolbox: build: fix import cli command. (_2025-01-26_)
- :toolbox: build: add excluded for scripts files. (_2025-01-25_)
- :toolbox: build: change icon prefix on pre-commit ci. (_2025-01-25_)
- :toolbox: build: add script path for run cli on local. (_2025-01-25_)
- :toolbox: build: update pyproject file. (_2025-01-25_)

### :postbox: Dependencies

- :pushpin: deps: remove more_itertools package from dependencies. (_2025-01-26_)

## 0.2.10

### :tada: Features

- :dart: feat: update setting on git pre-commit group. (_2025-01-25_)

### :book: Documents

- :page_facing_up: docs: update readme file. (_2025-01-25_)
- :page_facing_up: docs: update doc-string on git mod. (_2025-01-24_)
- :page_facing_up: docs: update doc-string on version mod. (_2025-01-24_)
- :page_facing_up: docs: update doc-string. (_2025-01-24_)

### :black_nib: Code Changes

- :test_tube: tests: add testcase on utils for make 100% coverage. (_2025-01-24_)
- :construction: refactored: 📦 bump more-itertools from 10.5.0 to 10.6.0 (_2025-01-20_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.12.2 to 1.12.3 (_2025-01-01_)
- :construction: refactored: 📦 update click requirement from <9.0.0,==8.1.7 to ==8.1.8 (_2024-12-23_)

## 0.2.9

### :book: Documents

- :page_facing_up: docs: update contribute topic in readme file. (_2024-12-12_)

### :black_nib: Code Changes

- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.11.0 to 1.12.2 (_2024-12-01_)
- :construction: refactored: ⬆ bump codecov/codecov-action from 4 to 5 (_2024-12-01_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.10.2 to 1.11.0 (_2024-11-01_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.10.0 to 1.10.2 (_2024-10-01_)

### :bug: Fix Bugs

- :gear: fixed: fix pre-commit config syntax for version 4.0.0. (_2024-10-08_)

## 0.2.8

### :tada: Features

- :dart: feat: commit message change add support for merge. (_2024-09-20_)

### :book: Documents

- :page_facing_up: docs: update readme docs that sync cli docs from package. (_2024-09-19_)

### :black_nib: Code Changes

- :construction: refactored: remove unuse cli command in version. (_2024-09-20_)
- :construction: refactored: remove log and init cli command. (_2024-09-19_)

### :postbox: Dependencies

- :pushpin: deps: remove tomli package from this project and use build-in instead. (_2024-09-20_)

## 0.2.7

### :tada: Features

- :dart: feat: add emojis args on the emoji module for dynamic passing emoji data. (_2024-09-19_)
- :dart: feat: add get git local config function. (_2024-09-19_)

### :book: Documents

- :page_facing_up: docs: update doc-string on cli command. (_2024-09-19_)

### :black_nib: Code Changes

- :construction: refactored: remove df and pf cli command. (_2024-09-19_)
- :construction: refactored: remove bn and tg cli command. (_2024-09-19_)

### :bug: Fix Bugs

- :gear: fixed: update id on python setup step. (_2024-09-17_)

### :package: Build & Workflow

- :toolbox: build: add python version 3.13 on pre-commit workflow. (_2024-09-17_)

## 0.2.6

### :book: Documents

- :page_facing_up: docs: update readme and add noted on version cli. (_2024-09-17_)

### :black_nib: Code Changes

- :construction: refactored: 📦 bump more-itertools from 10.4.0 to 10.5.0 (_2024-09-09_)

### :bug: Fix Bugs

- :gear: fixed: add option include-hidden-files on coverage workflow. (_2024-09-02_)

### :package: Build & Workflow

- :toolbox: build: add test matrix for python version 3.13. (_2024-09-17_)
- :toolbox: build: add debug command on coverage workflow. (_2024-09-02_)

## 0.2.5

### :book: Documents

- :page_facing_up: docs: update readme file. (_2024-09-02_)

### :black_nib: Code Changes

- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.9.0 to 1.10.0 (_2024-09-01_)
- :construction: refactored: 📦 bump more-itertools from 10.3.0 to 10.4.0 (_2024-08-12_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.8.14 to 1.9.0 (_2024-07-01_)
- :construction: refactored: 📦 bump more-itertools from 10.2.0 to 10.3.0 (_2024-06-17_)

### :bug: Fix Bugs

- :gear: fixed: add try-except for cove command. (_2024-06-09_)
- :gear: fixed: remove print statement. (_2024-05-05_)

## 0.2.4

### :bug: Fix Bugs

- :gear: fixed: remove dynamic tag from __about__ to fix value. (_2024-05-04_)

### :package: Build & Workflow

- :toolbox: build: chnage url for testpypi publish workflow. (_2024-05-04_)
- :toolbox: build: add tags regex for coverage workflow. (_2024-05-03_)
- :toolbox: build: add request package on coverage workflow. (_2024-05-03_)

## 0.2.3

### :book: Documents

- :page_facing_up: docs: update readme file that remove help command. (_2024-05-03_)
- :page_facing_up: docs: update description of this project for pypi. (_2024-05-02_)

### :package: Build & Workflow

- :toolbox: build: add gitignore for pdm and add requests package on test workflow. (_2024-05-03_)

## 0.2.2

### :book: Documents

- :page_facing_up: docs: update readme for add more detail. (_2024-05-02_)

### :black_nib: Code Changes

- :construction: refactored: remove optional dependencies that does not necessary. (_2024-05-02_)

### :package: Build & Workflow

- :toolbox: build: change build backend package from hatch to pdm. (_2024-05-02_)
- :toolbox: build: add environment on publish workflow. (_2024-05-02_)
- :toolbox: build: change timezone of dependabot. (_2024-05-02_)

## 0.2.1

### :tada: Features

- :dart: feat: add commit_prefix_force_fix config key for support force receive commit msg. (_2024-04-29_)

### :book: Documents

- :page_facing_up: docs: update mini-roadmap on README file. (_2024-04-25_)
- :page_facing_up: docs: add comment for profiling command raise error when does not set git config. (_2024-04-17_)
- :page_facing_up: docs: update README file for noted about migration roadmap. (_2024-04-14_)
- :page_facing_up: docs: update contributing and readme docs. (_2024-03-04_)
- :page_facing_up: docs: update README file. (_2024-03-03_)

### :black_nib: Code Changes

- :construction: refactored: 📦 bump mypy from 1.9.0 to 1.10.0 (_2024-04-29_)
- :construction: refactored: 📦 bump pytest from 8.1.1 to 8.2.0 (#66) (_2024-04-29_)
- :construction: refactored: 📦 bump coverage[toml] from 7.4.4 to 7.5.0 (_2024-04-29_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.8.12 to 1.8.14 (_2024-04-01_)
- :construction: refactored: 📦 bump coverage[toml] from 7.4.3 to 7.4.4 (_2024-03-18_)
- :construction: refactored: 📦 bump pytest from 8.1.0 to 8.1.1 (_2024-03-11_)
- :construction: refactored: 📦 bump mypy from 1.8.0 to 1.9.0 (_2024-03-11_)
- :construction: refactored: 📦 bump pytest from 8.0.2 to 8.1.0 (_2024-03-04_)

## 0.2.0

> [!WARNING]
> This version start support python version >= 3.9.13

### :black_nib: Code Changes

- :construction: refactored: upgrade python version from 38 to 39. (_2024-03-03_)
- :construction: refactored: 📦 bump pytest from 8.0.1 to 8.0.2 (_2024-02-26_)

## 0.1.10

> [!NOTE]
> This version combine fixed code from v0.1.9 post releases.

### 0.1.9.post2

### :bug: Fix Bugs

- :gear: fixed: add path param on download-artifact. (_2024-03-03_)

### 0.1.9.post1

### :bug: Fix Bugs

- :gear: fixed: remove ls coverage file step on coverage workflow. (_2024-03-03_)

### 0.1.9.post0

### :bug: Fix Bugs

- :gear: fixed: fix attr on download-artifact v4 does not use name for merge multiple. (_2024-03-03_)

## 0.1.9

### :tada: Features

- :dart: feat: add tg-bump command for auto create tag from latest after bumpping. (_2024-02-27_)
- :dart: feat: add cm-msg command for list commit prefixes. (_2024-02-19_)
- :dart: feat: add files param for bump version command for change version other files. (_2024-02-16_)

### :book: Documents

- :page_facing_up: docs: update option highlight for note on README file. (_2024-02-29_)
- :page_facing_up: docs: add noted on bump2version will change to new fork repo. (_2024-02-26_)
- :page_facing_up: docs: update README for more info of this project. (_2024-02-18_)
- :page_facing_up: docs: update README on pre-commit hook topic. (_2024-02-16_)

### :black_nib: Code Changes

- :test_tube: test: add testcase and comment for coverage. (_2024-03-03_)
- :construction: refactored: change the name of converage file store on coverage workflow. (_2024-03-02_)
- :construction: refactored: add merge multiple name of coverage file store on coverage workflow. (_2024-03-02_)
- :construction: refactored: ⬆ bump actions/upload-artifact from 3 to 4 (_2024-03-01_)
- :construction: refactored: ⬆ bump actions/download-artifact from 3 to 4 (_2024-03-01_)
- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.8.11 to 1.8.12 (_2024-03-01_)
- :test_tube: test: add more testcase for increase coverage value. (_2024-02-27_)
- :construction: refactored: 📦 bump coverage[toml] from 7.4.1 to 7.4.3 (_2024-02-26_)
- :construction: refactored: 📦 bump pytest from 8.0.0 to 8.0.1 (_2024-02-19_)
- :test_tube: test: add more testcases for support coverage. (_2024-02-17_)

### :package: Build & Workflow

- :toolbox: build: add emoji for issue template. (_2024-02-17_)
- :toolbox: build: fix desc of question template. (_2024-02-16_)
- :toolbox: build: add issue template for question. (_2024-02-16_)
- :toolbox: build: add question template. (_2024-02-16_)

## 0.1.8

### :black_nib: Code Changes

- :rewind: revert: revert change for ls command on pre-commit workflow. (_2024-02-16_)
- :test_tube: tests: add debug step for list file on local. (_2024-02-16_)
- :bookmark: Bump up to version 0.1.7.post1 -> 0.1.8. (_2024-02-16_)
- :construction: refactored: change option of pre-commit on workflow. (_2024-02-16_)
- :test_tube: test: add testcase for version commands. (_2024-02-16_)

### :bug: Fix Bugs

- :fire: hotfix: fixed ls command on ubuntu does not support. (_2024-02-16_)
- :gear: fixed: create pre-commit file on github action. (_2024-02-16_)
- :gear: fixed: remove debug code from git command. (_2024-02-14_)
- :gear: fixed: fix test shelf command does not find test file. (_2024-02-14_)
- :gear: fixed: run pre-commit all files for fix hooks. (_2024-02-13_)

### :package: Build & Workflow

- :toolbox: build: prepare pre-commit testing workflow. (_2024-02-16_)
- :toolbox: build: add checkout step before testing pre-commit. (_2024-02-16_)
- :toolbox: build: add parameter on pre-commit workflow for dynamic test. (_2024-02-16_)
- :toolbox: build: add coverage workflow for report quality of this proj. (_2024-02-16_)
- :toolbox: build: add pre-commit workflow that able to test hook from this repo. (_2024-02-14_)

## 0.1.7

### :book: Documents

- :page_facing_up: docs: update CONTRIBUTING file that relate with updated version. (_2024-02-13_)
- :page_facing_up: docs: update propose of this project include hooks. (_2024-02-13_)

### :black_nib: Code Changes

- :construction: refactored: change option and name of cm-previous command. (_2024-02-13_)
- :art: styled: add emoji to setting for reference. (_2024-02-13_)

### :bug: Fix Bugs

- :gear: fixed: fix get commit prefix config does not filter out duplicate value. (_2024-02-13_)

### :package: Build & Workflow

- :toolbox: build: edit config for override commit prefix group emoji. (_2024-02-13_)

## 0.1.6

### :tada: Features

- :dart: feat: add emoji on commit group when writing changelog file. (_2024-02-13_)

### :black_nib: Code Changes

- :construction: refactored: change emoji for commit prefix group. (_2024-02-13_)

### :card_file_box: Documents

- :page_facing_up: docs: update pre-commit hook topic on README file. (_2024-02-13_)

## 0.1.5.a1

### Fix Bugs

- :gear: fixed: fixed argument of cm command for receive extra arg. (_2024-02-13_)

## 0.1.5.a0

### Features

- :dart: feat: add pre-commit hook for external usage without install. (_2024-02-13_)

### Build & Workflow

- :toolbox: build: fixed config for hook to always run. (_2024-02-13_)

## 0.1.5

### Features

- :dart: feat: add git_demojize func for replace emoji value to str. (_2024-02-13_)
- :dart: feat: add emoji command that support convert emoji value on commit msg. (_2024-02-13_)
- :dart: feat: implement CommitPrefix and CommitPrefixGroup. (_2024-02-13_)
- :dart: feat: add CommitPrefix and CommitPrefixGroup dataclasses. (_2024-02-12_)

### Code Changes

- :construction: refactored: change list to tuple for mem save. (_2024-02-13_)

### Documents

- :page_facing_up: docs: update emoji command and config detail on README. (_2024-02-13_)

### Build & Workflow

- :toolbox: build: fixed deps on tests workflow. (_2024-02-13_)

## 0.1.4

### Features

- :dart: feat: add override commit prefix with any emoji and prefix values. (_2024-02-12_)

### Code Changes

- :test_tube: test: add testcase for override git commit prefix group. (_2024-02-12_)

### Documents

- :page_facing_up: docs: add configuration topic for help to change any config value. (_2024-02-12_)
- :page_facing_up: docs: update info for df command on git group in README. (_2024-02-12_)

## 0.1.3

### Features

- :dart: feat: add clean untrack files on cm-revert command. (_2024-02-12_)
- :dart: feat: add bump version support with datetime mode with pre value. (_2024-02-12_)
- :dart: feat: add bump version support with datetime mode. (_2024-02-12_)
- :dart: feat: add df command for show files change on previous commit. (_2024-02-12_)
- :dart: feat: update emoji for commit message fixing. (_2024-02-12_)

### Code Changes

- :construction: refactored: ⬆ bump actions/cache from 3 to 4 (_2024-02-01_)
- :construction: refactored: 📦 bump coverage[toml] from 7.4.0 to 7.4.1 (#39) (_2024-01-29_)
- :construction: refactored: 📦 bump pytest from 7.4.4 to 8.0.0 (_2024-01-29_)
- :construction: refactored: 📦 bump more-itertools from 10.1.0 to 10.2.0 (_2024-01-15_)

### Fix Bugs

- :gear: fixed: add dynamic value for regex on writer changelog func. (_2024-02-12_)

## 0.1.2

### Features

- :dart: feat: add deps emoji for update any thing that relate with package dependency. (_2023-12-16_)

### Code Changes

- :construction: refactored: ⬆ bump actions/setup-python from 4 to 5 (#33) (_2024-01-01_)
- :construction: refactored: fix typos (#32) (_2024-01-01_)
- :construction: refactored: 📦 bump pytest from 7.4.3 to 7.4.4 (_2024-01-01_)
- :construction: refactored: 📦 bump coverage[toml] from 7.3.4 to 7.4.0 (_2024-01-01_)
- :construction: refactored: 📦 bump coverage[toml] from 7.3.3 to 7.3.4 (_2023-12-27_)
- :construction: refactored: 📦 bump mypy from 1.7.1 to 1.8.0 (_2023-12-25_)
- :construction: refactored: 📦 bump coverage[toml] from 7.3.2 to 7.3.3 (_2023-12-18_)

### Fix Bugs

- :gear: fixed: add deleted file stage for bump2version process. (_2024-01-04_)

### Build & Workflow

- :toolbox: build: add python 3.12 for test workflow. (_2024-01-04_)

## 0.1.1

### Features

- :dart: feat: add dep common command for generate dependencies. (_2023-12-15_)
- :dart: feat: add command mg for merge with strategy. (_2023-12-15_)
- :dart: feat: add get_version method on BumpVerConf. (_2023-12-15_)

### Code Changes

- :construction: refactored: ⬆ bump pypa/gh-action-pypi-publish from 1.8.10 to 1.8.11 (_2023-12-01_)
- :construction: refactored: 📦 bump mypy from 1.7.0 to 1.7.1 (_2023-11-27_)
- :construction: refactored: 📦 bump mypy from 1.6.1 to 1.7.0 (_2023-11-13_)
- :construction: refactored: 📦 update pytest requirement from <8.0.0,==7.4.2 to ==7.4.3 (_2023-10-30_)
- :construction: refactored: 📦 bump mypy from 1.5.1 to 1.6.1 (_2023-10-23_)
- :construction: refactored: change logic of writer_changelog function. (_2023-10-22_)

### Documents

- :page_facing_up: docs: update README for a new git command. (_2023-12-15_)

### Fix Bugs

- :gear: fixed: add regex key when generate bump2version config file. (_2023-12-15_)

### Build & Workflow

- :toolbox: build: change frequency of dependabot from weekly to monthly. (_2023-11-22_)

## 0.1.0

### Features

- :dart: feat: add write all changelog option for re-write all logs to new file. (_2023-10-17_)
- :dart: feat: add tag from version cli for create git tag by __about__. (_2023-10-06_)

### Code Changes

- :construction: refactored: change the name of cli commands. (_2023-10-17_)
- :construction: refactored: change value on BumpVerConf obj in setting file. (_2023-10-16_)
- :construction: refactored: change print function to click.echo that recommend by click. (_2023-10-16_)
- :construction: refactored: 📦 bump mypy from 1.5.1 to 1.6.0 (#13) (_2023-10-16_)
- :construction: refactored: 📦 bump pre-commit from 3.4.0 to 3.5.0 (_2023-10-16_)
- :construction: refactored: 📦 bump coverage[toml] from 7.3.1 to 7.3.2 (_2023-10-09_)

### Documents

- :page_facing_up: docs: update doc-string on bump command. (_2023-10-17_)
- :page_facing_up: docs: update API commands on README file. (_2023-10-17_)

## 0.0.4

### Features

- :dart: feat: add git cmd for sync deleted tag from remote. (_2023-10-06_)
- :dart: feat: add init-conf Git command for set name and email on local. (_2023-09-14_)

### Code Changes

- :bookmark: Bump up to version 0.0.3 -> 0.0.4. (_2023-10-06_)
- :test_tube: test: update test-case for git cli. (_2023-10-06_)
- :construction: refactored: change test-case name and improve perf in git. (_2023-10-06_)
- :construction: refactored: add detail syntax for git commands. (_2023-09-26_)

### Documents

- :page_facing_up: docs: update feature on README. (_2023-10-06_)
- :page_facing_up: docs: add comment statement on cli command. (_2023-10-06_)
- :page_facing_up: docs: add doc-string and license message. (_2023-10-02_)
- :page_facing_up: docs: update CONTRIBUTING file for revise name and email in git. (_2023-09-14_)

### Fix Bugs

- :gear: fixed: add value for the Level enum before return. (_2023-10-06_)
- :gear: fixed: change make_color function that handle value of Enum. (_2023-10-06_)

## 0.0.3

### Features

- :dart: feat: add CONTRIBUTING file to this project. (_2023-09-12_)
- :dart: feat: add CONTRIBUTING file to this project. (_2023-09-12_)

### Code Changes

- :construction: refactor: [pre-commit.ci] auto fixes from pre-commit.com hooks (_2023-09-12_)
- :construction: refactor: [pre-commit.ci] pre-commit autoupdate (_2023-09-12_)
- :test_tube: test: add test case for git cli. (_2023-09-09_)
- :test_tube: test: add test case for git cli. (_2023-09-09_)
- :construction: refactor: ⬆ bump actions/checkout from 3 to 4 (_2023-09-08_)
- :test_tube: test: add parameter for pre-commit ci workflow. (_2023-09-08_)

### Documents

- :page_facing_up: docs: edit README file and add more information of this project. (_2023-09-12_)

### Build & Workflow

- :toolbox: build: add skip pytest from local repo of pre-commit config. (_2023-09-12_)
- :toolbox: build: add pip ecosystem in dependabot. (_2023-09-08_)
- :package: build: create dependabot.yml (_2023-09-08_)

## 0.0.2

### Documents

- :page_facing_up: docs: update README and deps package on pyproject. (_2023-09-08_)

### Build & Workflow

- :toolbox: build: change install deps package GitHub workflow. (_2023-09-08_)

## 0.0.1

### Features

- :dart: feat: first initial the main code to this repo. (_2023-09-08_)

### Code Changes

- :construction: refactored: change version of initial stage to 0.0.0. (_2023-09-08_)
- :construction: refactor: Initial commit (_2023-09-08_)

### Documents

- :page_facing_up: docs: edit name in README file and remove un-use deps package. (_2023-09-08_)

### Build & Workflow

- :toolbox: build: add GitHub workflows for test and publish. (_2023-09-08_)
