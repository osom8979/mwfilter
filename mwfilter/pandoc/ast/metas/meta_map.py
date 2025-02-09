# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict

from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.pandoc.ast.metas.parser import parse_meta_value


@dataclass
class MetaMap(MetaValue[Dict[str, MetaValue]]):
    content: Dict[str, MetaValue] = field(default_factory=dict)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls({k: parse_meta_value(v) for k, v in e.items()})

    def serialize(self):
        return {k: v.serialize() for k, v in self.content.items()}
