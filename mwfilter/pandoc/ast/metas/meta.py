# -*- coding: utf-8 -*-

from typing import Dict

from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.pandoc.ast.metas.parser import parse_meta_value


class Meta(Dict[str, MetaValue]):
    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls({k: parse_meta_value(v) for k, v in e.items()})

    def serialize(self):
        return {k: v.serialize() for k, v in self.items()}

    @property
    def has_redirect(self):
        return self.__contains__("redirect")
