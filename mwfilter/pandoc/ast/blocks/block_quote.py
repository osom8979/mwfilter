# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks


@dataclass
class BlockQuote(Block):
    """Block quote (list of blocks)"""

    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_blocks(e))
