# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines


@dataclass
class Span(Inline):
    """Generic inline container with attributes"""

    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        inlines = parse_inlines(e[1])
        return cls(attr, inlines)
