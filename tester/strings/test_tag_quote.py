# -*- coding: utf-8 -*-

from io import StringIO
from unittest import TestCase, main

from mwfilter.strings.tag_quote import tag_quote


class TagQuoteTestCase(TestCase):
    def test_block_style(self):
        buffer = StringIO()
        with tag_quote(buffer, "a"):
            buffer.write("Text")
        self.assertEqual('<a markdown="1">\nText\n</a>\n', buffer.getvalue())

    def test_inline_style(self):
        buffer = StringIO()
        with tag_quote(buffer, "a", newline=None):
            buffer.write("Text")
        self.assertEqual('<a markdown="1">Text</a>', buffer.getvalue())

    def test_no_markdown(self):
        buffer = StringIO()
        with tag_quote(buffer, "a", markdown=None, newline=None):
            buffer.write("Text")
        self.assertEqual("<a>Text</a>", buffer.getvalue())

    def test_more_attributes(self):
        buffer = StringIO()
        with tag_quote(buffer, "a", markdown=None, newline=None, style="color:red"):
            buffer.write("Text")
        self.assertEqual('<a style="color:red">Text</a>', buffer.getvalue())


if __name__ == "__main__":
    main()
