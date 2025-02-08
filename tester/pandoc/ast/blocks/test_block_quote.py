# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.block_quote import BlockQuote
from mwfilter.pandoc.ast.blocks.para import Para
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


class BlockQuoteTestCase(TestCase):
    def test_default(self):
        text = "<blockquote>AAA</blockquote>"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, BlockQuote)
        self.assertEqual(1, len(b0.blocks))

        b0b0 = b0.blocks[0]
        self.assertIsInstance(b0b0, Para)
        self.assertEqual(1, len(b0b0.inlines))

        b0b0i0 = b0b0.inlines[0]
        self.assertIsInstance(b0b0i0, Str)
        self.assertEqual("AAA", b0b0i0.text)


if __name__ == "__main__":
    main()
