# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Dict, Sequence, Type

from mwfilter.pandoc.ast.blocks.block import Block


@lru_cache
def block_classes() -> Sequence[Type[Block]]:
    # [IMPORTANT] Avoid 'circular import' issues
    from mwfilter.pandoc.ast.blocks.block_quote import BlockQuote
    from mwfilter.pandoc.ast.blocks.bullet_list import BulletList
    from mwfilter.pandoc.ast.blocks.code_block import CodeBlock
    from mwfilter.pandoc.ast.blocks.definition_list import DefinitionList
    from mwfilter.pandoc.ast.blocks.div import Div
    from mwfilter.pandoc.ast.blocks.figure import Figure
    from mwfilter.pandoc.ast.blocks.header import Header
    from mwfilter.pandoc.ast.blocks.horizontal_rule import HorizontalRule
    from mwfilter.pandoc.ast.blocks.line_block import LineBlock
    from mwfilter.pandoc.ast.blocks.ordered_list import OrderedList
    from mwfilter.pandoc.ast.blocks.para import Para
    from mwfilter.pandoc.ast.blocks.plain import Plain
    from mwfilter.pandoc.ast.blocks.raw_block import RawBlock
    from mwfilter.pandoc.ast.blocks.table import Table

    return (
        Table,
        BlockQuote,
        BulletList,
        CodeBlock,
        DefinitionList,
        Div,
        Figure,
        Header,
        HorizontalRule,
        LineBlock,
        OrderedList,
        Para,
        Plain,
        RawBlock,
    )


@lru_cache
def block_map() -> Dict[str, Type[Block]]:
    return {cls.__name__: cls for cls in block_classes()}


def parse_block(e) -> Block:
    assert isinstance(e, dict)
    e_type = e.get("t")
    e_content = e.get("c")
    assert isinstance(e_type, str)
    return block_map()[e_type].parse_object(e_content)


def parse_blocks(e):
    assert isinstance(e, list)
    return list(parse_block(item) for item in e)


def parse_blockss(e):
    assert isinstance(e, list)
    return list(parse_blocks(item) for item in e)
