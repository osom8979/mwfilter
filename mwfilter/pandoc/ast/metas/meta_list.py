# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.pandoc.ast.metas.parser import parse_meta_value
from mwfilter.types.override import override


@dataclass
class MetaList(MetaValue[List[MetaValue]]):
    content: List[MetaValue] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        return cls(list(parse_meta_value(item) for item in e))

    @override
    def serialize(self):
        return list(v.serialize() for v in self.content)
