# -*- coding: utf-8 -*-

from unittest import TestCase, main

import mwfilter.pandoc.ast.inlines.str_
from mwfilter.pandoc import ast


class BlockQuoteTestCase(TestCase):
    def test_default(self):
        text = "<blockquote>AAA</blockquote>"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.BlockQuote)
        self.assertEqual(1, len(b0.blocks))

        b0b0 = b0.blocks[0]
        self.assertIsInstance(b0b0, ast.Para)
        self.assertEqual(1, len(b0b0.inlines))

        b0b0i0 = b0b0.inlines[0]
        self.assertIsInstance(b0b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("AAA", b0b0i0.text)


if __name__ == "__main__":
    main()
