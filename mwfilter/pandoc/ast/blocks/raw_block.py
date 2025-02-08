# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.blocks.block import Block


@dataclass
class RawBlock(Block):
    """Raw block"""

    format: str = field(default_factory=str)
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        format_ = e[0]
        assert isinstance(format_, str)
        text = e[1]
        assert isinstance(text, str)
        return cls(format_, text)
