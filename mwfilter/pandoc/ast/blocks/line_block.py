# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inliness
from mwfilter.types.override import override


@dataclass
class LineBlock(Block):
    """Multiple non-breaking lines"""

    inliness: List[List[Inline]] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        return cls(parse_inliness(e))
