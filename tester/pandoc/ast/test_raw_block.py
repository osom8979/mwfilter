# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc import ast


class RawBlockTestCase(TestCase):
    def test_default(self):
        text = "<html>AAA</html>"

        obj = ast.Pandoc.parse_text(text)
        self.assertTrue(3, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, ast.RawBlock)
        self.assertEqual("html", b0.format)
        self.assertEqual("<html>", b0.text)

        b1 = obj.blocks[1]
        self.assertIsInstance(b1, ast.Para)
        self.assertEqual(1, len(b1.inlines))

        b1i0 = b1.inlines[0]
        self.assertIsInstance(b1i0, ast.Str)
        self.assertEqual("AAA", b1i0.text)

        b2 = obj.blocks[2]
        self.assertIsInstance(b2, ast.RawBlock)
        self.assertEqual("html", b2.format)
        self.assertEqual("</html>", b2.text)


if __name__ == "__main__":
    main()
