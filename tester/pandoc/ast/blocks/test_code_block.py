# -*- coding: utf-8 -*-

from unittest import TestCase, main

from mwfilter.pandoc.ast.blocks.code_block import CodeBlock
from mwfilter.pandoc.ast.pandoc import Pandoc


class CodeBlockTestCase(TestCase):
    def test_default(self):
        text = "<pre>TEST</pre>"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, CodeBlock)
        self.assertFalse(b0.attr.identifier)
        self.assertFalse(b0.attr.classes)
        self.assertFalse(b0.attr.pairs)
        self.assertEqual("TEST", b0.text)

    def test_python(self):
        text = "<syntaxhighlight lang='python'>print('AAA')</syntaxhighlight>"

        obj = Pandoc.parse_text(text)
        self.assertTrue(1, len(obj.blocks))

        b0 = obj.blocks[0]
        self.assertIsInstance(b0, CodeBlock)
        self.assertFalse(b0.attr.identifier)
        self.assertEqual(1, len(b0.attr.classes))
        self.assertEqual("python", b0.attr.classes[0])
        self.assertFalse(b0.attr.pairs)
        self.assertEqual("print('AAA')", b0.text)


if __name__ == "__main__":
    main()
