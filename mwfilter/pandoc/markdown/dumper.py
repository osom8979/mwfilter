# -*- coding: utf-8 -*-

from copy import copy
from io import StringIO
from typing import Any, Callable, Dict, Optional, Type

from mwfilter.mw.page_meta import PageMeta

# AST: Blocks
from mwfilter.pandoc.ast.blocks.block import Block
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

# AST: Inlines
from mwfilter.pandoc.ast.inlines.cite import Cite
from mwfilter.pandoc.ast.inlines.code import Code
from mwfilter.pandoc.ast.inlines.emph import Emph
from mwfilter.pandoc.ast.inlines.image import Image
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.line_break import LineBreak
from mwfilter.pandoc.ast.inlines.link import Link
from mwfilter.pandoc.ast.inlines.math import Math
from mwfilter.pandoc.ast.inlines.note import Note
from mwfilter.pandoc.ast.inlines.quoted import Quoted
from mwfilter.pandoc.ast.inlines.raw_inline import RawInline
from mwfilter.pandoc.ast.inlines.small_caps import SmallCaps
from mwfilter.pandoc.ast.inlines.soft_break import SoftBreak
from mwfilter.pandoc.ast.inlines.space import Space
from mwfilter.pandoc.ast.inlines.span import Span
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.inlines.strikeout import Strikeout
from mwfilter.pandoc.ast.inlines.strong import Strong
from mwfilter.pandoc.ast.inlines.subscript import Subscript
from mwfilter.pandoc.ast.inlines.superscript import Superscript
from mwfilter.pandoc.ast.inlines.underline import Underline

# AST
from mwfilter.pandoc.ast.pandoc import Pandoc


class PandocToMarkdownDumper:
    _block_map: Dict[Type[Block], Callable[[Block], None]]
    _inline_map: Dict[Type[Inline], Callable[[Inline], None]]

    def __init__(self, no_yaml_frontmatter=False):
        self._no_yaml_frontmatter = no_yaml_frontmatter
        self._buffer = StringIO()
        self._block_map = {
            BlockQuote: self.on_block_quote,
            BulletList: self.on_bullet_list,
            CodeBlock: self.on_code_block,
            DefinitionList: self.on_definition_list,
            Div: self.on_div,
            Figure: self.on_figure,
            Header: self.on_header,
            HorizontalRule: self.on_horizontal_rule,
            LineBlock: self.on_line_block,
            OrderedList: self.on_ordered_list,
            Para: self.on_para,
            Plain: self.on_plain,
            RawBlock: self.on_raw_block,
            Table: self.on_table,
        }
        self._inline_map = {
            Cite: self.on_cite,
            Code: self.on_code,
            Emph: self.on_emph,
            Image: self.on_image,
            LineBreak: self.on_line_break,
            Link: self.on_link,
            Math: self.on_math,
            Note: self.on_note,
            Quoted: self.on_quoted,
            RawInline: self.on_raw_inline,
            SmallCaps: self.on_small_caps,
            SoftBreak: self.on_soft_break,
            Space: self.on_space,
            Span: self.on_span,
            Str: self.on_str_,
            Strikeout: self.on_strikeout,
            Strong: self.on_strong,
            Subscript: self.on_subscript,
            Superscript: self.on_superscript,
            Underline: self.on_underline,
        }

    @staticmethod
    def update_page_meta(pandoc: Pandoc, meta: PageMeta):
        pandoc.meta["title"] = {"t": "Str", "c": meta.name}
        pandoc.meta["date"] = {"t": "Str", "c": meta.date}
        alias = list()
        for a in meta.alias:
            alias.append({"t": "Str", "c": a})
        pandoc.meta["alias"] = {"t": "List", "c": alias}

    def dump(self, pandoc: Pandoc, meta: Optional[PageMeta] = None) -> str:
        if meta is not None:
            pandoc = copy(pandoc)
            self.update_page_meta(pandoc, meta)
        self.on_pandoc(pandoc)
        return self._buffer.getvalue()

    def on_pandoc(self, e: Pandoc) -> None:
        self.on_meta(e.meta)
        for block in e.blocks:
            self.on_block(block)

    def on_meta(self, e: Dict[str, Any]) -> None:
        # buffer = StringIO()
        # buffer.write("---\n")
        # buffer.write(f"title: {self.name}\n")
        # buffer.write(f"date: {self.date}\n")
        # if self.meta.alias:
        #     buffer.write("alias:\n")
        #     for alias in self.meta.alias:
        #         buffer.write(f"  - {alias}\n")
        # buffer.write("---\n")
        # buffer.write("\n")
        pass

    # ----------------------------------------------------------------------------------
    # Blocks
    # ----------------------------------------------------------------------------------

    def on_block(self, e: Block) -> None:
        if callback := self._block_map.get(type(e)):
            callback(e)
        else:
            raise TypeError(f"Unsupported block type: {type(e).__name__}")

    def on_block_quote(self, e: BlockQuote) -> None:
        pass

    def on_bullet_list(self, e: BulletList) -> None:
        pass

    def on_code_block(self, e: CodeBlock) -> None:
        pass

    def on_definition_list(self, e: DefinitionList) -> None:
        pass

    def on_div(self, e: Div) -> None:
        pass

    def on_figure(self, e: Figure) -> None:
        pass

    def on_header(self, e: Header) -> None:
        pass

    def on_horizontal_rule(self, e: HorizontalRule) -> None:
        pass

    def on_line_block(self, e: LineBlock) -> None:
        pass

    def on_ordered_list(self, e: OrderedList) -> None:
        pass

    def on_para(self, e: Para) -> None:
        pass

    def on_plain(self, e: Plain) -> None:
        pass

    def on_raw_block(self, e: RawBlock) -> None:
        pass

    def on_table(self, e: Table) -> None:
        pass

    # ----------------------------------------------------------------------------------
    # Inlines
    # ----------------------------------------------------------------------------------

    def on_inline(self, e: Inline) -> None:
        if callback := self._inline_map.get(type(e)):
            callback(e)
        else:
            raise TypeError(f"Unsupported inline type: {type(e).__name__}")

    def on_cite(self, e: Cite) -> None:
        pass

    def on_code(self, e: Code) -> None:
        pass

    def on_emph(self, e: Emph) -> None:
        pass

    def on_image(self, e: Image) -> None:
        pass

    def on_line_break(self, e: LineBreak) -> None:
        pass

    def on_link(self, e: Link) -> None:
        pass

    def on_math(self, e: Math) -> None:
        pass

    def on_note(self, e: Note) -> None:
        pass

    def on_quoted(self, e: Quoted) -> None:
        pass

    def on_raw_inline(self, e: RawInline) -> None:
        pass

    def on_small_caps(self, e: SmallCaps) -> None:
        pass

    def on_soft_break(self, e: SoftBreak) -> None:
        pass

    def on_space(self, e: Space) -> None:
        pass

    def on_span(self, e: Span) -> None:
        pass

    def on_str_(self, e: Str) -> None:
        pass

    def on_strikeout(self, e: Strikeout) -> None:
        pass

    def on_strong(self, e: Strong) -> None:
        pass

    def on_subscript(self, e: Subscript) -> None:
        pass

    def on_superscript(self, e: Superscript) -> None:
        pass

    def on_underline(self, e: Underline) -> None:
        pass


def mediawiki_to_markdown(mediawiki_context: str) -> str:
    dumper = PandocToMarkdownDumper()
    pandoc = Pandoc.parse_text(mediawiki_context)
    return dumper.dump(pandoc)
