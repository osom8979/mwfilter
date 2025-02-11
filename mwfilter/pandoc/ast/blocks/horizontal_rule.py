# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.types.override import override


@dataclass
class HorizontalRule(Block):
    """Horizontal rule"""

    @classmethod
    @override
    def parse_object(cls, e):
        assert e is None
        return cls()
