# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.inlines.inline import Inline


@dataclass
class Note(Inline):
    """Footnote or endnote"""

    blocks: List["Block"] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        # [IMPORTANT] Avoid 'circular import' issues
        from mwfilter.pandoc.ast import parse_blocks

        assert isinstance(e, list)
        return cls(parse_blocks(e))
