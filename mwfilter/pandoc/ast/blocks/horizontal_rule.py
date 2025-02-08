# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.blocks.block import Block


@dataclass
class HorizontalRule(Block):
    """Horizontal rule"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()
