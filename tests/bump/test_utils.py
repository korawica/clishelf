import pytest

from clishelf.bump.bump import assemble_context
from clishelf.bump.utils import ConfFile, kv_str
from clishelf.bump.version_part import VersionConfig


@pytest.fixture(scope="function")
def vs_conf():
    return VersionConfig(
        parse=r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)",
        serialize=["{major}.{minor}.{patch}"],
        search="{current_version}",
        replace="{new_version}",
        part_configs={},
    )


def test_replace_updates_file(tmp_path, vs_conf):
    p = tmp_path / "file.txt"
    p.write_text("version = 1.2.3\n")
    cf = ConfFile(p, vs_conf)
    ctx = assemble_context()
    cf.replace("1.2.3", "1.2.4", ctx)
    assert "1.2.4" in p.read_text()


def test_replace_dry_run_does_not_modify(tmp_path, vs_conf):
    p = tmp_path / "file2.txt"
    p.write_text("version = 1.2.3\n")
    cf = ConfFile(p, vs_conf)
    ctx = assemble_context()
    cf.replace("1.2.3", "1.2.4", ctx, dry_run=True)
    assert "1.2.3" in p.read_text()
    assert "1.2.4" not in p.read_text()


def test_should_contain_version_raises(tmp_path, vs_conf):
    p = tmp_path / "file3.txt"
    p.write_text("version = 0.0.1\n")
    cf = ConfFile(p, vs_conf)
    ctx = assemble_context()
    import pytest

    with pytest.raises(ValueError):
        cf.should_contain_version("1.0.0", ctx)


def test_kv_str():
    assert kv_str({"foo": 1, "bar": "baz"}) == "foo=1, bar=baz"
    assert kv_str(1) == "1"
