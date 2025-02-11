# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.types.override import override


@dataclass
class MetaBlocks(MetaValue[List[Block]]):
    content: List[Block] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        return cls(parse_blocks(e))

    @override
    def serialize(self):
        return list(str(b) for b in self.content)
