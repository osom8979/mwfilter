# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.types.override import override


@dataclass
class MetaInlines(MetaValue[List[Inline]]):
    content: List[Inline] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        return cls(parse_inlines(e))

    @override
    def serialize(self):
        return list(str(i) for i in self.content)
