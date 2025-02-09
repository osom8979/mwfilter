# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.metas.meta_value import MetaValue


@dataclass
class MetaString(MetaValue[str]):
    content: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, str)
        return cls(e)

    def serialize(self):
        return self.content
