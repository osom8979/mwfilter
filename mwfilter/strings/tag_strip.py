# -*- coding: utf-8 -*-

from html.parser import HTMLParser
from io import StringIO


class TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._buffer = StringIO()

    def handle_data(self, data):
        self._buffer.write(data)

    def getvalue(self):
        return self._buffer.getvalue()


def strip_tags(text: str):
    parser = TagStripper()
    parser.feed(text)
    return parser.getvalue()
