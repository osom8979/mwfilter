# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc import ast


class BulletListTestCase(TestCase):
    def test_default(self):
        text = "* A"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.BulletList)
        self.assertEqual(1, len(b0.blockss))

        b0bs0 = b0.blockss[0]
        self.assertIsInstance(b0bs0, list)
        self.assertEqual(1, len(b0bs0))
        b0bs00 = b0bs0[0]

        self.assertIsInstance(b0bs00, ast.Plain)
        self.assertEqual(1, len(b0bs00.inlines))
        b0bs00i0 = b0bs00.inlines[0]
        self.assertIsInstance(b0bs00i0, ast.Str)
        self.assertEqual("A", b0bs00i0.text)


if __name__ == "__main__":
    main()
