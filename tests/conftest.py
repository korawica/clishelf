import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_path() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def make_yaml_conf(test_path):
    conf_file_mock: Path = test_path / ".clishelf.yaml"

    if Path().resolve().samefile(test_path):

        conf_file: Path = test_path.parent / ".clishelf.yaml"

        if conf_file.exists():
            shutil.copy(conf_file, conf_file_mock)

    yield

    conf_file_mock.unlink(missing_ok=True)
