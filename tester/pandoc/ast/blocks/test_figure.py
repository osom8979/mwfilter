# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.figure import Figure
from mwfilter.pandoc.ast.blocks.plain import Plain
from mwfilter.pandoc.ast.inlines.image import Image
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


class FigureTestCase(TestCase):
    def test_default(self):
        text = "[[Image:A.png]]"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, Figure)
        self.assertTrue(b0.attr.is_empty)
        self.assertIsNone(b0.caption.short_caption)
        self.assertEqual(1, len(b0.caption.blocks))

        b0b0 = b0.blocks[0]
        self.assertIsInstance(b0b0, Plain)
        self.assertEqual(1, len(b0b0.inlines))

        b0b0i0 = b0b0.inlines[0]
        self.assertIsInstance(b0b0i0, Image)
        self.assertTrue(b0b0i0.attr.is_empty)
        self.assertFalse(b0b0i0.inlines)
        self.assertEqual("A.png", b0b0i0.target.url)
        self.assertEqual("A.png", b0b0i0.target.title)

        b0cb0 = b0.caption.blocks[0]
        self.assertIsInstance(b0cb0, Plain)
        self.assertEqual(1, len(b0cb0.inlines))

        b0cb0i0 = b0cb0.inlines[0]
        self.assertIsInstance(b0cb0i0, Str)
        self.assertEqual("A.png", b0cb0i0.text)


if __name__ == "__main__":
    main()
