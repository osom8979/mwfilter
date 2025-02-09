# -*- coding: utf-8 -*-

from copy import copy
from io import StringIO
from typing import Callable, Dict, Optional, Sequence, Type, Union

import yaml

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
from mwfilter.pandoc.ast.enums import MathType

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

# AST: ETC
from mwfilter.pandoc.ast.interface import DumperInterface

# AST: Metas
from mwfilter.pandoc.ast.metas.meta import Meta
from mwfilter.pandoc.ast.metas.meta_blocks import MetaBlocks
from mwfilter.pandoc.ast.metas.meta_bool import MetaBool
from mwfilter.pandoc.ast.metas.meta_inlines import MetaInlines
from mwfilter.pandoc.ast.metas.meta_list import MetaList
from mwfilter.pandoc.ast.metas.meta_map import MetaMap
from mwfilter.pandoc.ast.metas.meta_string import MetaString
from mwfilter.pandoc.ast.metas.meta_value import MetaValue
from mwfilter.pandoc.ast.pandoc import Pandoc
from mwfilter.types.override import override


class PandocToMarkdownDumper(DumperInterface):
    _metas: Dict[Type[MetaValue], Callable[[MetaValue], str]]
    _blocks: Dict[Type[Block], Callable[[Block], str]]
    _inlines: Dict[Type[Inline], Callable[[Inline], str]]

    def __init__(self, *, no_abspath=False, no_yaml_frontmatter=False):
        self._no_abspath = no_abspath
        self._no_yaml_frontmatter = no_yaml_frontmatter
        self._metas = {
            MetaBlocks: self.on_meta_blocks,
            MetaBool: self.on_meta_bool,
            MetaInlines: self.on_meta_inlines,
            MetaList: self.on_meta_list,
            MetaMap: self.on_meta_map,
            MetaString: self.on_meta_string,
        }
        self._blocks = {
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
        self._inlines = {
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
            Str: self.on_str,
            Strikeout: self.on_strikeout,
            Strong: self.on_strong,
            Subscript: self.on_subscript,
            Superscript: self.on_superscript,
            Underline: self.on_underline,
        }

    @staticmethod
    def update_page_meta(pandoc: Pandoc, meta: PageMeta):
        if meta.name:
            pandoc.meta["title"] = MetaString(meta.name)
        if meta.date:
            pandoc.meta["date"] = MetaString(meta.date)
        if meta.alias:
            pandoc.meta["alias"] = MetaList(list(MetaString(a) for a in meta.alias))

    def dump(self, pandoc: Pandoc, meta: Optional[PageMeta] = None) -> str:
        if meta is not None:
            pandoc = copy(pandoc)
            self.update_page_meta(pandoc, meta)
        return self.on_pandoc(pandoc)

    def dump_blocks(self, blocks: Sequence[Block]) -> str:
        buffer = StringIO()
        for block in blocks:
            buffer.write(self.on_block(block))
        return buffer.getvalue()

    def dump_inlines(self, inlines: Sequence[Inline]) -> str:
        buffer = StringIO()
        for inline in inlines:
            buffer.write(self.on_inline(inline))
        return buffer.getvalue()

    def dump_items_quote(
        self,
        items: Union[str, Block, Inline, Sequence[Block], Sequence[Inline]],
        begin: str,
        end: Optional[str] = None,
    ) -> str:
        buffer = StringIO()
        buffer.write(begin)
        if isinstance(items, str):
            buffer.write(items)
        elif isinstance(items, Block):
            buffer.write(self.on_block(items))
        elif isinstance(items, Inline):
            buffer.write(self.on_inline(items))
        elif isinstance(items, Sequence):
            if all(isinstance(i, Inline) for i in items):
                buffer.write(self.dump_inlines(items))  # type: ignore[arg-type]
            elif all(isinstance(b, Block) for b in items):
                buffer.write(self.dump_blocks(items))  # type: ignore[arg-type]
            else:
                raise TypeError("Inline and Block elements should not be mixed")
        else:
            raise TypeError(f"Unsupported item type: {type(items).__name__}")
        buffer.write(end if end else begin)
        return buffer.getvalue()

    def dump_items_tag_quote(
        self,
        tag: str,
        items: Union[str, Block, Inline, Sequence[Block], Sequence[Inline]],
        **kwargs: str,
    ) -> str:
        buffer = StringIO()
        buffer.write(f"<{tag}")
        if kwargs:
            for k, v in kwargs.items():
                buffer.write(f' {k}="{v}"')
        buffer.write(">")
        return self.dump_items_quote(
            items=items,
            begin=buffer.getvalue(),
            end=f"</{tag}>",
        )

    @override
    def on_pandoc(self, e: Pandoc) -> str:
        buffer = StringIO()
        if not self._no_yaml_frontmatter:
            buffer.write(self.on_meta(e.meta))
        for block in e.blocks:
            text = self.on_block(block)
            buffer.write(text)
        return buffer.getvalue()

    # ----------------------------------------------------------------------------------
    # Metas
    # ----------------------------------------------------------------------------------

    @override
    def on_meta(self, e: Meta) -> str:
        if not e:
            return ""
        buffer = StringIO()
        buffer.write("---\n")
        buffer.write(yaml.dump(e.serialize(), default_flow_style=False))
        buffer.write("---\n\n")
        return buffer.getvalue()

    @override
    def on_meta_value(self, e: MetaValue) -> str:
        if callback := self._metas.get(type(e)):
            return callback(e)
        else:
            raise TypeError(f"Unsupported block type: {type(e).__name__}")

    @override
    def on_meta_blocks(self, e: MetaBlocks) -> str:
        raise NotImplementedError

    @override
    def on_meta_bool(self, e: MetaBool) -> str:
        raise NotImplementedError

    @override
    def on_meta_inlines(self, e: MetaInlines) -> str:
        raise NotImplementedError

    @override
    def on_meta_list(self, e: MetaList) -> str:
        raise NotImplementedError

    @override
    def on_meta_map(self, e: MetaMap) -> str:
        raise NotImplementedError

    @override
    def on_meta_string(self, e: MetaString) -> str:
        raise NotImplementedError

    # ----------------------------------------------------------------------------------
    # Blocks
    # ----------------------------------------------------------------------------------

    @override
    def on_block(self, e: Block) -> str:
        if callback := self._blocks.get(type(e)):
            return callback(e)
        else:
            raise TypeError(f"Unsupported block type: {type(e).__name__}")

    @override
    def on_block_quote(self, e: BlockQuote) -> str:
        return self.dump_items_tag_quote("blockquote", e.blocks)

    @override
    def on_bullet_list(self, e: BulletList) -> str:
        buffer = StringIO()
        buffer.write("<ul>\n")
        for blocks in e.blockss:
            buffer.write("<li>\n")
            for block in blocks:
                buffer.write(self.on_block(block))
            buffer.write("</li>\n")
        buffer.write("</ul>\n")
        return buffer.getvalue()

    @override
    def on_code_block(self, e: CodeBlock) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        buffer.write("```\n")
        buffer.write(e.text)
        buffer.write("```\n")
        return buffer.getvalue()

    @override
    def on_definition_list(self, e: DefinitionList) -> str:
        buffer = StringIO()
        buffer.write("<dl>\n")
        for item in e.items:
            inlines = item[0]
            blockss = item[1]

            buffer.write("<dt>\n")
            for inline in inlines:
                buffer.write(self.on_inline(inline))
            buffer.write("</dt>\n")

            for blocks in blockss:
                buffer.write("<dd>\n")
                try:
                    for block in blocks:
                        text = self.on_block(block)
                        buffer.write(text)
                finally:
                    buffer.write("</dd>\n")
            buffer.write("\n")
        buffer.write("</dl>\n")
        return buffer.getvalue()

    @override
    def on_div(self, e: Div) -> str:
        buffer = StringIO()
        buffer.write("<div>\n")
        buffer.write(self.dump_blocks(e.blocks))
        buffer.write("</div>\n")
        return buffer.getvalue()

    @override
    def on_figure(self, e: Figure) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        buffer.write("<figure>\n")
        buffer.write(self.dump_blocks(e.blocks))
        if e.caption.short_caption or e.caption.blocks:
            buffer.write("<figcaption>\n")
            if e.caption.short_caption:
                buffer.write(self.dump_inlines(e.caption.short_caption.inlines))
            if e.caption.blocks:
                buffer.write(self.dump_blocks(e.caption.blocks))
            buffer.write("</figcaption>\n")
        buffer.write("</figure>\n")
        return buffer.getvalue()

    @override
    def on_header(self, e: Header) -> str:
        assert 1 <= e.level
        buffer = StringIO()
        buffer.write(f"<h{e.level}>\n")
        buffer.write(self.dump_inlines(e.inlines))
        buffer.write(f"</h{e.level}>\n")
        return buffer.getvalue()

    @override
    def on_horizontal_rule(self, e: HorizontalRule) -> str:
        return "<hr />\n"

    @override
    def on_line_block(self, e: LineBlock) -> str:
        buffer = StringIO()
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nobr
        buffer.write('<span style="white-space: nowrap;">\n')
        for inlines in e.inliness:
            buffer.write(self.dump_inlines(inlines))
        buffer.write("</span>\n")
        return buffer.getvalue()

    @override
    def on_ordered_list(self, e: OrderedList) -> str:
        buffer = StringIO()
        buffer.write(f'<ol start="{e.list_attributes.start_number}">\n')
        for blocks in e.blockss:
            buffer.write("<li>\n")
            for block in blocks:
                buffer.write(self.on_block(block))
            buffer.write("</li>\n")
        buffer.write("</ol>\n")
        return buffer.getvalue()

    @override
    def on_para(self, e: Para) -> str:
        buffer = StringIO()
        buffer.write("<p>\n")
        buffer.write(self.dump_inlines(e.inlines))
        buffer.write("</p>\n")
        return buffer.getvalue()

    @override
    def on_plain(self, e: Plain) -> str:
        buffer = StringIO()
        buffer.write("<pre>\n")
        buffer.write(self.dump_inlines(e.inlines))
        buffer.write("</pre>\n")
        return buffer.getvalue()

    @override
    def on_raw_block(self, e: RawBlock) -> str:
        buffer = StringIO()
        buffer.write("<pre>\n")
        buffer.write(e.text)
        buffer.write("</pre>\n")
        return buffer.getvalue()

    @override
    def on_table(self, e: Table) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        buffer.write("<table>\n")
        if e.caption.short_caption or e.caption.blocks:
            buffer.write("<caption>\n")
            if e.caption.short_caption:
                buffer.write(self.dump_inlines(e.caption.short_caption.inlines))
            if e.caption.blocks:
                buffer.write(self.dump_blocks(e.caption.blocks))
            buffer.write("</caption>\n")

        if e.table_head:
            buffer.write("<thead>\n")
            if not e.table_head.attr.is_empty:
                raise NotImplementedError
            for row in e.table_head.rows:
                buffer.write("<tr>\n")
                if not row.attr.is_empty:
                    raise NotImplementedError
                for cell in row.cells:
                    if not cell.attr.is_empty:
                        raise NotImplementedError
                    # alignment = cell.alignment  # TODO
                    # row_span = cell.row_span  # TODO
                    # col_span = cell.col_span  # TODO
                    buffer.write("<td>\n")
                    buffer.write(self.dump_blocks(cell.blocks))
                    buffer.write("</td>\n")
                buffer.write("</tr>\n")
            buffer.write("</thead>\n")

        for tbody in e.table_body:
            buffer.write("<tbody>\n")
            if not tbody.attr.is_empty:
                raise NotImplementedError
            # row_head_columns = tbody.row_head_columns  # TODO

            for row in tbody.header_rows:
                buffer.write("<tr>\n")
                if not row.attr.is_empty:
                    raise NotImplementedError
                for cell in row.cells:
                    if not cell.attr.is_empty:
                        raise NotImplementedError
                    # alignment = cell.alignment  # TODO
                    # row_span = cell.row_span  # TODO
                    # col_span = cell.col_span  # TODO
                    buffer.write("<td>\n")
                    buffer.write(self.dump_blocks(cell.blocks))
                    buffer.write("</td>\n")
                buffer.write("</tr>\n")

            for row in tbody.body_rows:
                buffer.write("<tr>\n")
                if not row.attr.is_empty:
                    raise NotImplementedError
                for cell in row.cells:
                    if not cell.attr.is_empty:
                        raise NotImplementedError
                    # alignment = cell.alignment  # TODO
                    # row_span = cell.row_span  # TODO
                    # col_span = cell.col_span  # TODO
                    buffer.write("<td>\n")
                    buffer.write(self.dump_blocks(cell.blocks))
                    buffer.write("</td>\n")
                buffer.write("</tr>\n")

            buffer.write("</tbody>\n")

        if e.table_foot:
            buffer.write("<tfoot>\n")
            if not e.table_foot.attr.is_empty:
                raise NotImplementedError
            for row in e.table_foot.rows:
                buffer.write("<tr>\n")
                if not row.attr.is_empty:
                    raise NotImplementedError
                for cell in row.cells:
                    if not cell.attr.is_empty:
                        raise NotImplementedError
                    # alignment = cell.alignment  # TODO
                    # row_span = cell.row_span  # TODO
                    # col_span = cell.col_span  # TODO
                    buffer.write("<td>\n")
                    buffer.write(self.dump_blocks(cell.blocks))
                    buffer.write("</td>\n")
                buffer.write("</tr>\n")
            buffer.write("</tfoot>\n")

        buffer.write("</table>\n")
        return buffer.getvalue()

    # ----------------------------------------------------------------------------------
    # Inlines
    # ----------------------------------------------------------------------------------

    @override
    def on_inline(self, e: Inline) -> str:
        if callback := self._inlines.get(type(e)):
            return callback(e)
        else:
            raise TypeError(f"Unsupported inline type: {type(e).__name__}")

    @override
    def on_cite(self, e: Cite) -> str:
        return self.dump_items_tag_quote("cite", e.inlines)

    @override
    def on_code(self, e: Code) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        return self.dump_items_tag_quote("code", e.text)

    @override
    def on_emph(self, e: Emph) -> str:
        return self.dump_items_tag_quote("em", e.inlines)

    @override
    def on_image(self, e: Image) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        title = e.target.title
        src = e.target.url
        buffer.write(f'<img src="{src}" title="{title}">')
        buffer.write(self.dump_inlines(e.inlines))
        buffer.write("</img>")
        return buffer.getvalue()

    @override
    def on_line_break(self, e: LineBreak) -> str:
        return "<br />"

    @override
    def on_link(self, e: Link) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        buffer.write("[")
        buffer.write(self.dump_inlines(e.inlines))
        link = e.target.as_markdown_link(no_abspath=self._no_abspath)
        buffer.write(f"]({link})")
        return buffer.getvalue()

    @override
    def on_math(self, e: Math) -> str:
        assert e.math_type in (MathType.DisplayMath, MathType.InlineMath)
        token = "$$\n" if e.math_type == MathType.DisplayMath else "$"
        buffer = StringIO()
        buffer.write(token)
        buffer.write(e.text.strip())
        buffer.write("\n")
        buffer.write(token)
        return buffer.getvalue()

    @override
    def on_note(self, e: Note) -> str:
        raise NotImplementedError

    @override
    def on_quoted(self, e: Quoted) -> str:
        # e.quote_type  # TODO
        return self.dump_items_tag_quote("q", e.inlines)

    @override
    def on_raw_inline(self, e: RawInline) -> str:
        raise NotImplementedError

    @override
    def on_small_caps(self, e: SmallCaps) -> str:
        return self.dump_items_tag_quote("small", e.inlines)

    @override
    def on_soft_break(self, e: SoftBreak) -> str:
        return "\n"

    @override
    def on_space(self, e: Space) -> str:
        return "&nbsp;"

    @override
    def on_span(self, e: Span) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        return self.dump_items_tag_quote("span", e.inlines)

    @override
    def on_str(self, e: Str) -> str:
        return e.text

    @override
    def on_strikeout(self, e: Strikeout) -> str:
        return self.dump_items_tag_quote("s", e.inlines)

    @override
    def on_strong(self, e: Strong) -> str:
        return self.dump_items_tag_quote("strong", e.inlines)

    @override
    def on_subscript(self, e: Subscript) -> str:
        return self.dump_items_tag_quote("sub", e.inlines)

    @override
    def on_superscript(self, e: Superscript) -> str:
        return self.dump_items_tag_quote("sup", e.inlines)

    @override
    def on_underline(self, e: Underline) -> str:
        return self.dump_items_tag_quote("u", e.inlines)


def mediawiki_to_markdown(mediawiki_context: str) -> str:
    dumper = PandocToMarkdownDumper()
    pandoc = Pandoc.parse_text(mediawiki_context)
    return dumper.dump(pandoc)
