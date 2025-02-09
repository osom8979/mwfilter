# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.metas.meta_value import MetaValue


@dataclass
class MetaBool(MetaValue[bool]):
    content: bool = False

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, bool)
        return cls(e)
