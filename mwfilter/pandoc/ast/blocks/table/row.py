# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.table.cell import Cell


@dataclass
class Row:
    """A table row."""

    attr: Attr = field(default_factory=Attr)
    cells: List[Cell] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        cells = Cell.parse_object_with_list(e[1])
        return cls(attr, cells)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)
