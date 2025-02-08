# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.header import Header
from mwfilter.pandoc.ast.inlines.link import Link
from mwfilter.pandoc.ast.inlines.space import Space
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


class HeaderTestCase(TestCase):
    def test_default(self):
        text = "== BBB [[Page|Title]] =="

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, Header)
        self.assertEqual(2, b0.level)
        self.assertEqual("bbb_title", b0.attr.identifier)
        self.assertFalse(b0.attr.classes)
        self.assertFalse(b0.attr.pairs)
        self.assertTrue(3, len(b0.inlines))

        b0i0 = b0.inlines[0]
        self.assertIsInstance(b0i0, Str)
        self.assertEqual("BBB", b0i0.text)

        b0i1 = b0.inlines[1]
        self.assertIsInstance(b0i1, Space)

        b0i2 = b0.inlines[2]
        self.assertIsInstance(b0i2, Link)
        self.assertFalse(b0i2.attr.identifier)
        self.assertFalse(b0i2.attr.classes)
        self.assertFalse(b0i2.attr.pairs)
        self.assertEqual(1, len(b0i2.inlines))
        self.assertEqual("Page", b0i2.target.url)
        self.assertTrue(b0i2.target.is_wikilink)

        b0i2i0 = b0i2.inlines[0]
        self.assertIsInstance(b0i2i0, Str)
        self.assertEqual("Title", b0i2i0.text)


if __name__ == "__main__":
    main()
