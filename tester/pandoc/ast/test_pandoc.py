# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.pandoc import Pandoc


class PandocTestCase(TestCase):
    def test_default(self):
        obj = Pandoc.parse_text("A")
        self.assertTupleEqual((1, 23, 1), obj.pandoc_api_version)
        self.assertFalse(obj.meta)
        self.assertTrue(1, len(obj.blocks))


if __name__ == "__main__":
    main()
