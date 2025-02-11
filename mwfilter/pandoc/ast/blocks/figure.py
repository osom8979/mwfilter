# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.pandoc.ast.caption import Caption
from mwfilter.types.override import override


@dataclass
class Figure(Block):
    """Figure, with attributes, caption, and content (list of blocks)"""

    attr: Attr = field(default_factory=Attr)
    caption: Caption = field(default_factory=Caption)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        attr = Attr.parse_object(e[0])
        caption = Caption.parse_object(e[1])
        blocks = parse_blocks(e[2])
        return cls(attr, caption, blocks)
