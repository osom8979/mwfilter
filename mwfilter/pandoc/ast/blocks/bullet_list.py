# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blockss
from mwfilter.types.override import override


@dataclass
class BulletList(Block):
    """Bullet list (list of items, each a list of blocks)"""

    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        return cls(parse_blockss(e))
