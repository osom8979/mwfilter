# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.types.override import override


@dataclass
class BlockQuote(Block):
    """Block quote (list of blocks)"""

    blocks: List[Block] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        return cls(parse_blocks(e))
