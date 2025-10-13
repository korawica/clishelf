from pathlib import Path

import pytest

from clishelf.bump.bump import (
    assemble_context,
    bump_version_by_part_or_literal,
    replace_version_in_files,
)
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
