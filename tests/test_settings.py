import unittest
from datetime import datetime
from unittest.mock import patch

import clishelf.settings as settings


class SettingsTestCase(unittest.TestCase):
    def test_bump_version_setting(self):
        bump_setting = settings.BumpVerConf

        self.assertEqual(bump_setting.regex, bump_setting.get_regex())
        self.assertEqual(
            bump_setting.regex_dt,
            bump_setting.get_regex(is_dt=True),
        )

        update_dt_pre = bump_setting.update_dt_pre
        self.assertEqual("20240102.1", update_dt_pre("20240102"))
        self.assertEqual("20240102.6", update_dt_pre("20240102.5"))
        with self.assertRaises(ValueError):
            bump_setting.update_dt_pre("202401.post")

    def test_bump_version_get_version(self):
        bump_setting = settings.BumpVerConf
        rs = bump_setting.get_version(
            version=3,
            params={
                "version": "",
                "changelog": "",
                "file": "",
            },
        )
        self.assertEqual(
            rs,
            bump_setting.v1.format(
                changelog="",
                main=bump_setting.main.format(
                    version="",
                    msg=bump_setting.msg,
                    regex=bump_setting.regex,
                    file="",
                ),
            ),
        )

    @patch("clishelf.settings.datetime.datetime")
    def test_bump_version_get_version_dt(self, mock_datetime):
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
        self.assertEqual(
            rs,
            bump_setting.v2.format(
                changelog="",
                main=bump_setting.main_dt.format(
                    version="",
                    new_version="20240101",
                    msg=bump_setting.msg,
                    regex=bump_setting.regex_dt,
                    file="",
                ),
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
        self.assertEqual(
            rs,
            bump_setting.v2.format(
                changelog="",
                main=bump_setting.main_dt.format(
                    version="20240101",
                    new_version="20240101.1",
                    msg=bump_setting.msg,
                    regex=bump_setting.regex_dt,
                    file="",
                ),
            ),
        )

        with self.assertRaises(ValueError):
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
