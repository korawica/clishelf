import unittest

import clishelf.settings as settings


class SettingsTestCase(unittest.TestCase):
    def test_bump_version_update_dt_pre(self):
        result = settings.BumpVerConf.update_dt_pre("20230101")
        self.assertEqual("20230101.1", result)

        result = settings.BumpVerConf.update_dt_pre("20230101.99")
        self.assertEqual("20230101.100", result)
