# -*- coding: utf-8 -*-

import urllib.parse
from dataclasses import dataclass, field
from io import StringIO

from mwfilter.strings.remove_slash import remove_prefix_slashes


@dataclass
class Target:
    """Link target (URL, title)."""

    url: str = field(default_factory=str)
    title: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        url = e[0]
        title = e[1]
        assert isinstance(url, str)
        assert isinstance(title, str)
        return cls(url, title)

    @property
    def is_wikilink(self):
        return self.title == "wikilink"

    def as_markdown_link(self, *, no_extension=False, no_abspath=False):
        if not self.is_wikilink:
            return self.url

        if self.url.startswith("#"):
            return self.url  # Fragment Link

        wikilink = remove_prefix_slashes(self.url)
        if not wikilink:
            raise ValueError("Links consisting solely of slashes are not allowed.")

        link_items = wikilink.split("#", maxsplit=1)
        if len(link_items) == 1:
            link = link_items[0]
            anchor = str()
        else:
            assert len(link_items) == 2
            link = link_items[0]
            anchor = link_items[1]
            assert anchor.startswith("#")

        buffer = StringIO()
        if not no_abspath:
            buffer.write("/")
        buffer.write(urllib.parse.quote(link))
        if not no_extension:
            buffer.write(".md")
        if anchor:
            buffer.write(anchor)
        return buffer.getvalue()
