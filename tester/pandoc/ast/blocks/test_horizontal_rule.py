# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.horizontal_rule import HorizontalRule
from mwfilter.pandoc.ast.pandoc import Pandoc


class HorizontalRuleTestCase(TestCase):
    def test_default(self):
        text = "----"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, HorizontalRule)


if __name__ == "__main__":
    main()
