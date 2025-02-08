# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.para import Para
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


class ParaTestCase(TestCase):
    def test_default(self):
        text = "AAA"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, Para)
        self.assertTrue(1, len(b0.inlines))

        b0i0 = b0.inlines[0]
        self.assertIsInstance(b0i0, Str)
        self.assertEqual("AAA", b0i0.text)


if __name__ == "__main__":
    main()
