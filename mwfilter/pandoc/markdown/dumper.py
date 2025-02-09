# -*- coding: utf-8 -*-

from io import StringIO
from typing import Optional

from mwfilter.mw.page_meta import PageMeta
from mwfilter.pandoc.ast.pandoc import Pandoc


class PandocToMarkdownDumper:
    def __init__(self):
        self._buffer = StringIO()

    def dump(self, pandoc: Pandoc, meta: Optional[PageMeta] = None) -> str:
        self.on_pandoc(pandoc)
        return self._buffer.getvalue()

    def on_pandoc(self, e: Pandoc) -> None:
        pass


def mediawiki_to_markdown(mediawiki_context: str) -> str:
    dumper = PandocToMarkdownDumper()
    pandoc = Pandoc.parse_text(mediawiki_context)
    return dumper.dump(pandoc)
