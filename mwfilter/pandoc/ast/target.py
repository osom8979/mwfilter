# -*- coding: utf-8 -*-

import urllib.parse
from dataclasses import dataclass, field
from io import StringIO
from typing import Optional, Set

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

    def as_markdown_link(
        self,
        *,
        no_extension=False,
        no_abspath=False,
        filenames: Optional[Set[str]] = None,
    ):
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

        if self.url.startswith("/"):
            filename = link
        else:
            # -----------------------------------------------
            # MediaWiki articles start with a capital letter.
            filename = link[0].upper() + link[1:]
            # -----------------------------------------------

        filename = filename.replace(" ", "_")
        if filenames and filename not in filenames:
            raise FileNotFoundError(f"Not found link: '{link}'")

        buffer = StringIO()
        if not no_abspath:
            buffer.write("/")
        buffer.write(urllib.parse.quote(filename))
        if not no_extension:
            buffer.write(".md")
        if anchor:
            buffer.write("#")
            buffer.write(anchor)
        return buffer.getvalue()
