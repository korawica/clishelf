from pathlib import Path

import tomli
import tomli_w

from clishelf.bump.conf import load_config, save_config
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
        obj = tomli.load(f)

    assert obj["bumpversion"]["current_version"] == "0.1.1"
    assert obj["bumpversion"]["serialize"] == ["{major}.{minor}.{patch}"]
