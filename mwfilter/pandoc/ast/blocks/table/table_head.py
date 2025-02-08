# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.table.row import Row


@dataclass
class TableHead:
    """The head of a table."""

    attr: Attr = field(default_factory=Attr)
    rows: List[Row] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        rows = Row.parse_object_with_list(e[1])
        return cls(attr, rows)
