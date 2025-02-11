# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.types.override import override


@dataclass
class Header(Block):
    """Header - level (integer) and text (inlines)"""

    level: int = 0
    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        level = e[0]
        assert isinstance(level, int)
        attr = Attr.parse_object(e[1])
        inlines = parse_inlines(e[2])
        return cls(level, attr, inlines)
