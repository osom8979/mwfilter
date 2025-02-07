# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc import ast


class TableTestCase(TestCase):
    def test_default(self):
        text = "{|\n|+C\n|-\n!H\n|-\n|D\n|}"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.Table)
        self.assertTrue(b0.attr.is_empty)
        self.assertIsNone(b0.caption.short_caption)
        self.assertEqual(1, len(b0.caption.blocks))

        b0cb0 = b0.caption.blocks[0]
        self.assertIsInstance(b0cb0, ast.Plain)
        self.assertEqual(1, len(b0cb0.inlines))

        b0cb0i0 = b0cb0.inlines[0]
        self.assertIsInstance(b0cb0i0, ast.Str)
        self.assertEqual("C", b0cb0i0.text)


if __name__ == "__main__":
    main()
