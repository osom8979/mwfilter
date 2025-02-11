# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.pandoc.ast.target import Target
from mwfilter.types.override import override


@dataclass
class Link(Inline):
    """Hyperlink: alt text (list of inlines), target"""

    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)
    target: Target = field(default_factory=Target)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        attr = Attr.parse_object(e[0])
        inlines = parse_inlines(e[1])
        target = Target.parse_object(e[2])
        return cls(attr, inlines, target)
