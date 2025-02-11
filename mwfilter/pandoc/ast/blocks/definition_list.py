# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Tuple

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blockss
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.types.override import override


@dataclass
class DefinitionList(Block):
    """
    Definition list.
    Each list item is a pair consisting of a term (a list of inlines)
    and one or more definitions (each a list of blocks)
    """

    items: List[Tuple[List[Inline], List[List[Block]]]] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        return cls([(parse_inlines(i), parse_blockss(b)) for i, b in e])
