# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.table.row import Row
from mwfilter.pandoc.ast.blocks.table.row_head_columns import RowHeadColumns


@dataclass
class TableBody:
    """
    A body of a table, with an intermediate head, intermediate body,
    and the specified number of row header columns in the intermediate body.

    Warning:
        The <thead>, <tbody>, <tfoot>, <colgroup>, and <col> elements are currently not
        supported in MediaWiki
    """

    attr: Attr = field(default_factory=Attr)
    row_head_columns: RowHeadColumns = field(default_factory=RowHeadColumns)
    header_rows: List[Row] = field(default_factory=list)
    body_rows: List[Row] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 4
        attr = Attr.parse_object(e[0])
        row_head_columns = RowHeadColumns.parse_object(e[1])
        header_rows = Row.parse_object_with_list(e[2])
        body_rows = Row.parse_object_with_list(e[3])
        return cls(attr, row_head_columns, header_rows, body_rows)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)
