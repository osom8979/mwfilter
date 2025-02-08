# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.blocks.table.col_width import ColWidth
from mwfilter.pandoc.ast.enums import Alignment


@dataclass
class ColSpec:
    """The specification for a single table column."""

    alignment: Alignment = Alignment.AlignDefault
    col_width: ColWidth = field(default_factory=ColWidth)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        alignment = Alignment.parse_object(e[0])
        col_width = ColWidth.parse_object(e[1])
        return cls(alignment, col_width)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)
