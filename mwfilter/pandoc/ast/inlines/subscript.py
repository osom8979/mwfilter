# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines


@dataclass
class Subscript(Inline):
    """Subscripted text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))
