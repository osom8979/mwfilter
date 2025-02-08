# -*- coding: utf-8 -*-

from dataclasses import dataclass, field


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
