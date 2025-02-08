# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.pandoc.ast.blocks.table.col_span import ColSpan
from mwfilter.pandoc.ast.blocks.table.row_span import RowSpan
from mwfilter.pandoc.ast.enums import Alignment


@dataclass
class Cell:
    """A table cell."""

    attr: Attr = field(default_factory=Attr)
    alignment: Alignment = Alignment.AlignDefault
    row_span: RowSpan = field(default_factory=RowSpan)
    col_span: ColSpan = field(default_factory=ColSpan)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 5
        attr = Attr.parse_object(e[0])
        alignment = Alignment.parse_object(e[1])
        row_span = RowSpan.parse_object(e[2])
        col_span = ColSpan.parse_object(e[3])
        blocks = parse_blocks(e[4])
        return cls(attr, alignment, row_span, col_span, blocks)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)
