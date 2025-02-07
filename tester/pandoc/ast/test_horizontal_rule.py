# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc import ast


class HorizontalRuleTestCase(TestCase):
    def test_default(self):
        text = "----"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.HorizontalRule)


if __name__ == "__main__":
    main()
