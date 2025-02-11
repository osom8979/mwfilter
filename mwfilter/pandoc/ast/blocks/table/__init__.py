# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.table.col_spec import ColSpec
from mwfilter.pandoc.ast.blocks.table.table_body import TableBody
from mwfilter.pandoc.ast.blocks.table.table_foot import TableFoot
from mwfilter.pandoc.ast.blocks.table.table_head import TableHead
from mwfilter.pandoc.ast.caption import Caption
from mwfilter.types.override import override


@dataclass
class Table(Block):
    """
    Table, with attributes, caption, optional short caption, column alignments and
    widths (required), table head, table bodies, and table foot
    """

    attr: Attr = field(default_factory=Attr)
    caption: Caption = field(default_factory=Caption)
    col_specs: List[ColSpec] = field(default_factory=list)
    table_head: TableHead = field(default_factory=TableHead)
    table_body: List[TableBody] = field(default_factory=list)
    table_foot: TableFoot = field(default_factory=TableFoot)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 6
        attr = Attr.parse_object(e[0])
        caption = Caption.parse_object(e[1])
        col_specs = ColSpec.parse_object_with_list(e[2])
        table_head_ = TableHead.parse_object(e[3])
        table_body_ = TableBody.parse_object_with_list(e[4])
        table_foot_ = TableFoot.parse_object(e[5])
        return cls(attr, caption, col_specs, table_head_, table_body_, table_foot_)
