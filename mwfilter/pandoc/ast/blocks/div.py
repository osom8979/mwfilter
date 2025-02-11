# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.types.override import override


@dataclass
class Div(Block):
    """Generic block container with attributes"""

    attr: Attr = field(default_factory=Attr)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        blocks = parse_blocks(e[1])
        return cls(attr, blocks)
