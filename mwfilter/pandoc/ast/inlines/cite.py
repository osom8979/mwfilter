# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.citation import Citation
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.types.override import override


@dataclass
class Cite(Inline):
    """Citation (list of inlines)"""

    citations: List[Citation] = field(default_factory=list)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        citations = Citation.parse_object_with_list(e[0])
        inlines = parse_inlines(e[1])
        return cls(citations, inlines)
