# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.types.override import override


@dataclass
class Code(Inline):
    """Inline code (literal)"""

    attr: Attr = field(default_factory=Attr)
    text: str = field(default_factory=str)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        text = e[1]
        return cls(attr, text)
