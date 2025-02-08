# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Optional

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.pandoc.ast.short_caption import ShortCaption


@dataclass
class Caption:
    """The caption of a table or figure, with optional short caption."""

    short_caption: Optional[ShortCaption] = None
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        short_caption = e[0]
        assert isinstance(short_caption, (type(None), list))
        blocks = parse_blocks(e[1])
        return cls(short_caption, blocks)
