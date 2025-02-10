# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

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

# AST: Metas
from mwfilter.pandoc.ast.metas.meta import Meta
from mwfilter.pandoc.ast.metas.meta_blocks import MetaBlocks
from mwfilter.pandoc.ast.metas.meta_bool import MetaBool
from mwfilter.pandoc.ast.metas.meta_inlines import MetaInlines
from mwfilter.pandoc.ast.metas.meta_list import MetaList
from mwfilter.pandoc.ast.metas.meta_map import MetaMap
from mwfilter.pandoc.ast.metas.meta_string import MetaString
from mwfilter.pandoc.ast.metas.meta_value import MetaValue

# AST
from mwfilter.pandoc.ast.pandoc import Pandoc


class DumperInterface(ABC):
    @abstractmethod
    def on_pandoc(self, e: Pandoc) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta(self, e: Meta) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_value(self, e: MetaValue) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_blocks(self, e: MetaBlocks) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_bool(self, e: MetaBool) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_inlines(self, e: MetaInlines) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_list(self, e: MetaList) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_map(self, e: MetaMap) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_meta_string(self, e: MetaString) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_block(self, e: Block) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_block_quote(self, e: BlockQuote) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_bullet_list(self, e: BulletList) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_code_block(self, e: CodeBlock) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_definition_list(self, e: DefinitionList) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_div(self, e: Div) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_figure(self, e: Figure) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_header(self, e: Header) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_horizontal_rule(self, e: HorizontalRule) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_line_block(self, e: LineBlock) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_ordered_list(self, e: OrderedList) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_para(self, e: Para) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_plain(self, e: Plain) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_raw_block(self, e: RawBlock) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_table(self, e: Table) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_inline(self, e: Inline) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_cite(self, e: Cite) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_code(self, e: Code) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_emph(self, e: Emph) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_image(self, e: Image) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_line_break(self, e: LineBreak) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_link(self, e: Link) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_math(self, e: Math) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_note(self, e: Note) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_quoted(self, e: Quoted) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_raw_inline(self, e: RawInline) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_small_caps(self, e: SmallCaps) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_soft_break(self, e: SoftBreak) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_space(self, e: Space) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_span(self, e: Span) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_str(self, e: Str) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_strikeout(self, e: Strikeout) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_strong(self, e: Strong) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_subscript(self, e: Subscript) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_superscript(self, e: Superscript) -> str:
        raise NotImplementedError

    @abstractmethod
    def on_underline(self, e: Underline) -> str:
        raise NotImplementedError
