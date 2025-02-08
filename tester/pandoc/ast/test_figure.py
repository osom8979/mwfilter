# -*- coding: utf-8 -*-

from unittest import TestCase, main

import mwfilter.pandoc.ast.inlines.image
import mwfilter.pandoc.ast.inlines.str_
from mwfilter.pandoc import ast


class FigureTestCase(TestCase):
    def test_default(self):
        text = "[[Image:A.png]]"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.Figure)
        self.assertTrue(b0.attr.is_empty)
        self.assertIsNone(b0.caption.short_caption)
        self.assertEqual(1, len(b0.caption.blocks))

        b0b0 = b0.blocks[0]
        self.assertIsInstance(b0b0, ast.Plain)
        self.assertEqual(1, len(b0b0.inlines))

        b0b0i0 = b0b0.inlines[0]
        self.assertIsInstance(b0b0i0, mwfilter.pandoc.ast.inlines.image.Image)
        self.assertTrue(b0b0i0.attr.is_empty)
        self.assertFalse(b0b0i0.inlines)
        self.assertEqual("A.png", b0b0i0.target.url)
        self.assertEqual("A.png", b0b0i0.target.title)

        b0cb0 = b0.caption.blocks[0]
        self.assertIsInstance(b0cb0, ast.Plain)
        self.assertEqual(1, len(b0cb0.inlines))

        b0cb0i0 = b0cb0.inlines[0]
        self.assertIsInstance(b0cb0i0, mwfilter.pandoc.ast.inlines.str_.Str)
        self.assertEqual("A.png", b0cb0i0.text)


if __name__ == "__main__":
    main()
