# -*- coding: utf-8 -*-

from unittest import TestCase, main

import mwfilter.pandoc.ast.inlines.link
import mwfilter.pandoc.ast.inlines.space
import mwfilter.pandoc.ast.inlines.str_
from mwfilter.pandoc import ast


class HeaderTestCase(TestCase):
    def test_default(self):
        text = "== BBB [[Page|Title]] =="

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.Header)
        self.assertEqual(2, b0.level)
        self.assertEqual("bbb_title", b0.attr.identifier)
        self.assertFalse(b0.attr.classes)
        self.assertFalse(b0.attr.pairs)
        self.assertTrue(3, len(b0.inlines))

        b0i0 = b0.inlines[0]
        self.assertIsInstance(b0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("BBB", b0i0.text)

        b0i1 = b0.inlines[1]
        self.assertIsInstance(b0i1, mwfilter.pandoc.ast.inlines.space.Space)

        b0i2 = b0.inlines[2]
        self.assertIsInstance(b0i2, mwfilter.pandoc.ast.inlines.link.Link)
        self.assertFalse(b0i2.attr.identifier)
        self.assertFalse(b0i2.attr.classes)
        self.assertFalse(b0i2.attr.pairs)
        self.assertEqual(1, len(b0i2.inlines))
        self.assertEqual("Page", b0i2.target.url)
        self.assertTrue(b0i2.target.is_wikilink)

        b0i2i0 = b0i2.inlines[0]
        self.assertIsInstance(b0i2i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("Title", b0i2i0.text)


if __name__ == "__main__":
    main()
