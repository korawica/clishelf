from datetime import datetime
from unittest.mock import patch

import pytest

import clishelf.settings as settings


def test_bump_version_setting():
    bump_setting = settings.BumpVerConf

    assert bump_setting.regex == bump_setting.get_regex()
    assert bump_setting.regex_dt == bump_setting.get_regex(is_dt=True)

    update_dt_pre = bump_setting.update_dt_pre
    assert update_dt_pre("20240102") == "20240102.1"
    assert update_dt_pre("20240102.5") == "20240102.6"

    with pytest.raises(ValueError):
        bump_setting.update_dt_pre("202401.post")


def test_bump_version_get_version():
    bump_setting = settings.BumpVerConf
    rs = bump_setting.get_version(
        version=3,
        params={
            "version": "",
            "changelog": "",
            "file": "",
        },
    )
    assert rs == bump_setting.v1.format(
        changelog="",
        main=bump_setting.main.format(
            version="",
            msg=bump_setting.msg,
            regex=bump_setting.regex,
            file="",
        ),
    )


@patch("clishelf.settings.datetime.datetime")
def test_bump_version_get_version_dt(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1, 0, 0)
    bump_setting = settings.BumpVerConf
    rs = bump_setting.get_version(
        version=2,
        params={
            "version": "",
            "changelog": "",
            "file": "",
            "action": "date",
        },
        is_dt=True,
    )
    assert rs == bump_setting.v2.format(
        changelog="",
        main=bump_setting.main_dt.format(
            version="",
            new_version="20240101",
            msg=bump_setting.msg,
            regex=bump_setting.regex_dt,
            file="",
        ),
    )

    rs = bump_setting.get_version(
        version=2,
        params={
            "version": "20240101",
            "changelog": "",
            "file": "",
            "action": "pre",
        },
        is_dt=True,
    )
    assert rs == bump_setting.v2.format(
        changelog="",
        main=bump_setting.main_dt.format(
            version="20240101",
            new_version="20240101.1",
            msg=bump_setting.msg,
            regex=bump_setting.regex_dt,
            file="",
        ),
    )

    with pytest.raises(ValueError):
        bump_setting.get_version(
            version=2,
            params={
                "version": "20240101",
                "changelog": "",
                "file": "",
                "action": "post",
            },
            is_dt=True,
        )
