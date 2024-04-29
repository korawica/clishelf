import unittest

import clishelf.emoji as emoji


class EmojiTestCase(unittest.TestCase):
    def test_demojize_and_emojize(self):
        msg: str = "🎯 feat"
        self.assertEqual(":dart: feat", emoji.demojize(msg))
        self.assertIn("🎯", emoji.emojize(":dart:"))

        msg: str = "⬆️ deps: upgrade"
        self.assertEqual(":arrow_up: deps: upgrade", emoji.demojize(msg))
