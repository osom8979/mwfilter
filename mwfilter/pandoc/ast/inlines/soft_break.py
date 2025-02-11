# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.types.override import override


@dataclass
class SoftBreak(Inline):
    """Soft line break"""

    @classmethod
    @override
    def parse_object(cls, e):
        assert e is None
        return cls()
