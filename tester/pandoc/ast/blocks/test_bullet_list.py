# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.bullet_list import BulletList
from mwfilter.pandoc.ast.blocks.plain import Plain
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


class BulletListTestCase(TestCase):
    def test_default(self):
        text = "* A"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, BulletList)
        self.assertEqual(1, len(b0.blockss))

        b0bs0 = b0.blockss[0]
        self.assertIsInstance(b0bs0, list)
        self.assertEqual(1, len(b0bs0))
        b0bs00 = b0bs0[0]

        self.assertIsInstance(b0bs00, Plain)
        self.assertEqual(1, len(b0bs00.inlines))
        b0bs00i0 = b0bs00.inlines[0]
        self.assertIsInstance(b0bs00i0, Str)
        self.assertEqual("A", b0bs00i0.text)


if __name__ == "__main__":
    main()
