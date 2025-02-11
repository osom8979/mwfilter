# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.types.override import override


@dataclass
class MetaBool(MetaValue[bool]):
    content: bool = False

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, bool)
        return cls(e)

    @override
    def serialize(self):
        return self.content
