# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.inlines.inline import Inline


@dataclass
class Str(Inline):
    """Text (string)"""

    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, str)
        return cls(e)
