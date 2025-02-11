# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blockss
from mwfilter.pandoc.ast.list_attributes import ListAttributes
from mwfilter.types.override import override


@dataclass
class OrderedList(Block):
    """Ordered list (attributes and a list of items, each a list of blocks)"""

    list_attributes: ListAttributes = field(default_factory=ListAttributes)
    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        list_attributes = ListAttributes.parse_object(e[0])
        blockss = parse_blockss(e[1])
        return cls(list_attributes, blockss)
