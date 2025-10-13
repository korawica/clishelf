from pathlib import Path

import pytest

from clishelf.bump.bump import (
    assemble_context,
    bump_version_by_part_or_literal,
    replace_version_in_files,
)
from clishelf.bump.cli import write_bump_file
from clishelf.bump.conf import load_config
from clishelf.bump.utils import ConfFile
from clishelf.bump.version_part import VersionConfig


@pytest.fixture(scope="function")
def vc() -> VersionConfig:
    return VersionConfig(
        parse=r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)",
        serialize=["{major}.{minor}.{patch}"],
        search="{current_version}",
        replace="{new_version}",
        part_configs={},
    )


def test_bump_minor(vc: VersionConfig):
    context = assemble_context()
    current_obj, new_obj, new_version = bump_version_by_part_or_literal(
        vc, "2.7.1", "minor", None, context
    )
    assert new_version == "2.8.0"


def test_bump_with_explicit_new_version(vc):
    context = assemble_context()
    current_obj, new_obj, new_version = bump_version_by_part_or_literal(
        vc, "1.2.3", None, "2.0.0", context
    )
    assert new_version == "2.0.0"


def test_bump_invalid_no_part_or_new_version(vc):
    context = assemble_context()
    with pytest.raises(ValueError):
        bump_version_by_part_or_literal(vc, "1.2.3", None, None, context)


def test_replace_in_file(tmp_path: Path, vc):
    # create a dummy file containing "1.2.3"
    p = tmp_path / "sample.txt"
    p.write_text("version = 1.2.3\n")
    cf = ConfFile(p, vc)
    ctx = assemble_context()

    # replace 1.2.3 -> 1.2.4 (not dry-run)
    replace_version_in_files([cf], "1.2.3", "1.2.4", dry_run=False, context=ctx)
    content = p.read_text()
    assert "1.2.4" in content


def test_replace_dry_run_does_not_modify(tmp_path, vc):
    p = tmp_path / "sample2.txt"
    p.write_text("version = 1.2.3\n")
    cf = ConfFile(p, vc)
    ctx = assemble_context()

    replace_version_in_files([cf], "1.2.3", "1.2.4", dry_run=True, context=ctx)
    content = p.read_text()
    assert "1.2.3" in content
    assert "1.2.4" not in content


def test_bump_from_old_format(tmp_path: Path):
    bump_filepath = tmp_path / ".bumpversion.cfg"
    write_bump_file(
        param={
            "changelog": "CHANGELOG.md",
            "version": "0.0.1",
            "action": "minor",
            "file": "__about__.py",
        },
        version=1,
        is_dt=False,
        override_filepath=bump_filepath,
    )
    defaults, files, part_configs, cfg_path, cfg_format = load_config(
        str(bump_filepath)
    )
    # print(defaults)
    # print(bump_filepath.read_text())
    vc = VersionConfig(
        parse=defaults.get(
            "parse", r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
        ),
        serialize=defaults.get("serialize", ["{major}.{minor}.{patch}"]),
        search=defaults.get("search", "{current_version}"),
        replace=defaults.get("replace", "{new_version}"),
        part_configs=part_configs,
    )
    current_version: str = defaults.get("current_version")
    context = assemble_context()
    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, current_version, "minor", None, context
    )
    print(new_version_str)

    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, current_version, "prekind", None, context
    )
    print(new_version_str)
    #
    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, "0.0.1.a0", "patch", None, context
    )
    print(new_version_str)

    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, "0.0.1.a0", "pre", None, context
    )
    print(new_version_str)

    current_obj, new_obj, new_version_str = bump_version_by_part_or_literal(
        vc, "0.0.1.a0", "postkind", None, context
    )
    print(new_version_str)
