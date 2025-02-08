# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.inlines.inline import Inline


@dataclass
class SoftBreak(Inline):
    """Soft line break"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()
