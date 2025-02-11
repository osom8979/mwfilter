# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.types.override import override


@dataclass
class MetaString(MetaValue[str]):
    content: str = field(default_factory=str)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, str)
        return cls(e)

    @override
    def serialize(self):
        return self.content
