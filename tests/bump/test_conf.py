from pathlib import Path

import tomli_w

from clishelf.bump.cli import write_bump_file
from clishelf.bump.conf import load_config, save_config, tomllib
from clishelf.bump.version_part import ConfiguredPartConf


def test_load_toml_config(tmp_path: Path):
    toml_path = tmp_path / "bumpversion.toml"
    data = {
        "bumpversion": {
            "current_version": "0.1.0",
            "serialize": ["{major}.{minor}.{patch}"],
            "search": "{current_version}",
            "replace": "{new_version}",
        },
        "bumpversion:part:minor": {"values": ["0", "1", "2"]},
    }
    with toml_path.open("wb") as f:
        tomli_w.dump(data, f)

    defaults, files, part_configs, cfg_path, cfg_format = load_config(
        str(toml_path)
    )
    assert defaults["current_version"] == "0.1.0"
    assert "minor" in part_configs
    assert isinstance(part_configs["minor"], ConfiguredPartConf)
    assert cfg_format == "toml"


def test_save_config_updates_version(tmp_path: Path):
    toml_path = tmp_path / "bumpversion.toml"
    data = {
        "bumpversion": {
            "current_version": "0.1.0",
            "serialize": ["{major}.{minor}.{patch}"],
        }
    }
    with toml_path.open("wb") as f:
        tomli_w.dump(data, f)

    defaults, _, _, cfg_path, cfg_format = load_config(str(toml_path))
    save_config(cfg_path, cfg_format, defaults, "0.1.1", dry_run=False)
    with cfg_path.open("rb") as f:
        obj = tomllib.load(f)

    assert obj["bumpversion"]["current_version"] == "0.1.1"
    assert obj["bumpversion"]["serialize"] == ["{major}.{minor}.{patch}"]


def test_load_toml_config_from_old_format(tmp_path: Path):
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
    print(bump_filepath.read_text())
    defaults, files, part_configs, cfg_path, cfg_format = load_config(
        str(bump_filepath)
    )
    assert defaults == {
        "current_version": "0.0.1",
        "commit": "True",
        "tag": "False",
        "parse": "^\n(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)(\\.(?P<prekind>a|alpha|b|beta|d|dev|rc)(?P<pre>\\d+))?(\\.(?P<postkind>post)(?P<post>\\d+))?",
        "serialize": [
            "{major}.{minor}.{patch}.{prekind}{pre}.{postkind}{post}",
            "{major}.{minor}.{patch}.{prekind}{pre}",
            "{major}.{minor}.{patch}.{postkind}{post}",
            "{major}.{minor}.{patch}",
        ],
        "message": ":label: Bump up to version {current_version} -> {new_version}.",
    }
    assert cfg_path == bump_filepath
    assert cfg_format == "ini"

    defaults, _, _, cfg_path, cfg_format = load_config(str(bump_filepath))
    save_config(cfg_path, cfg_format, defaults, "0.1.1", dry_run=False)
