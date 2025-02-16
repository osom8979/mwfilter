# -*- coding: utf-8 -*-

from copy import copy
from io import StringIO
from types import MappingProxyType
from typing import Any, Callable, Dict, Final, List, Mapping, Optional, Sequence, Type

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
from mwfilter.pandoc.ast.blocks.table.cell import Cell
from mwfilter.pandoc.ast.blocks.table.row import Row

# AST: ETC
from mwfilter.pandoc.ast.dump.interface import DumperInterface
from mwfilter.pandoc.ast.enums import Alignment, MathType

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
from mwfilter.pandoc.ast.pandoc import Pandoc
from mwfilter.strings.tag_quote import tag_quote
from mwfilter.strings.tag_strip import strip_tags
from mwfilter.types.override import override

DEFAULT_REFERENCES_LOWER_TAGS: Final[Sequence[str]] = (
    "<references>",
    "<references/>",
    "<references />",
)

DEFAULT_CONVERT_RAW_TAGS: Final[MappingProxyType[str, str]] = MappingProxyType(
    {
        "<b>": "<strong>",
        "</b>": "</strong>",
        "<div>": "<div>",
        "</div>": "</div>",
        "<hr>": "<hr>",
        "<hr/>": "<hr/>",
        "<hr />": "<hr />",
        "<i>": "<em>",
        "</i>": "</em>",
        "<kbd>": "<kbd>",
        "</kbd>": "</kbd>",
        "<s>": "<del>",
        "</s>": "</del>",
        "<span>": "<span>",
        "</span>": "</span>",
        "<strong>": "<strong>",
        "</strong>": "</strong>",
        "<small>": '<span style="font-size:0.8em">',
        "</small>": "</span>",
        "<u>": "<u>",
        "</u>": "</u>",
    }
)


class PandocToMarkdownDumper(DumperInterface):
    _metas: Dict[Type[MetaValue], Callable[[MetaValue], str]]
    _blocks: Dict[Type[Block], Callable[[Block], str]]
    _inlines: Dict[Type[Inline], Callable[[Inline], str]]

    _footnotes: List[Note]

    def __init__(
        self,
        filenames: Optional[Sequence[str]] = None,
        *,
        no_abspath=False,
        no_extension=False,
        no_yaml_frontmatter=False,
        no_skip_attachments=False,
        no_references_to_footnotes=False,
        references_tags: Optional[Sequence[str]] = DEFAULT_REFERENCES_LOWER_TAGS,
        convert_raw_tags: Optional[Mapping[str, str]] = DEFAULT_CONVERT_RAW_TAGS,
    ):
        self._filenames = set(filenames if filenames else list())

        self._no_abspath = no_abspath
        # https://www.mkdocs.org/user-guide/writing-your-docs/#linking-to-pages
        # [Warning] Using absolute paths with links is not officially supported.
        # Relative paths are adjusted by MkDocs to ensure they are always relative to
        # the page. Absolute paths are not modified at all. This means that your links
        # using absolute paths might work fine in your local environment but they might
        # break once you deploy them to your production server.

        self._no_extension = no_extension
        self._no_yaml_frontmatter = no_yaml_frontmatter
        self._no_skip_attachments = no_skip_attachments
        self._no_references_to_footnotes = no_references_to_footnotes
        self._references_tags = list(references_tags if references_tags else list())
        self._convert_raw_tags = dict(convert_raw_tags if convert_raw_tags else dict())
        self._metas = self._create_metas_callbacks()
        self._blocks = self._create_blocks_callbacks()
        self._inlines = self._create_inline_callbacks()
        self._footnotes = list()

    def _create_metas_callbacks(self):
        return {
            MetaBlocks: self.on_meta_blocks,
            MetaBool: self.on_meta_bool,
            MetaInlines: self.on_meta_inlines,
            MetaList: self.on_meta_list,
            MetaMap: self.on_meta_map,
            MetaString: self.on_meta_string,
        }

    def _create_blocks_callbacks(self):
        return {
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

    def _create_inline_callbacks(self):
        return {
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
            pandoc.meta["lastmod"] = MetaString(meta.date)
        if meta.redirect and meta.redirect_pagename:
            pandoc.meta["template"] = MetaString("redirect.html")
            pandoc.meta["redirect"] = MetaString("/" + meta.redirect_pagename)
        if meta.authors:
            authors = list(MetaString(author) for author in meta.authors)
            pandoc.meta["authors"] = MetaList(authors)  # type: ignore[arg-type]

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

    @override
    def on_pandoc(self, e: Pandoc) -> str:
        buffer = StringIO()
        if not self._no_yaml_frontmatter:
            buffer.write(self.on_meta(e.meta))
            if e.meta.has_redirect:
                return buffer.getvalue()

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
        buffer.write(yaml.dump(e.serialize(), default_flow_style=False).strip())
        buffer.write("\n---\n\n")
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
        buffer = StringIO()
        with tag_quote(buffer, "blockquote"):
            buffer.write(self.dump_blocks(e.blocks))
        return buffer.getvalue()

    @override
    def on_bullet_list(self, e: BulletList) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "ul"):
            for blocks in e.blockss:
                with tag_quote(buffer, "li"):
                    buffer.write(self.dump_blocks(blocks))
        return buffer.getvalue()

    @override
    def on_code_block(self, e: CodeBlock) -> str:
        lang = e.attr.classes[0] if e.attr.classes else str()
        buffer = StringIO()
        buffer.write(f"```{lang}\n")
        buffer.write(e.text)
        buffer.write("\n```\n")
        return buffer.getvalue()

    @override
    def on_definition_list(self, e: DefinitionList) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "dl"):
            for item in e.items:
                inlines = item[0]
                blockss = item[1]
                with tag_quote(buffer, "dt"):
                    text = self.dump_inlines(inlines)
                    buffer.write(text)
                for blocks in blockss:
                    with tag_quote(buffer, "dd"):
                        buffer.write(self.dump_blocks(blocks))
        return buffer.getvalue()

    @override
    def on_div(self, e: Div) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "div"):
            buffer.write(self.dump_blocks(e.blocks))
        return buffer.getvalue()

    @override
    def on_figure(self, e: Figure) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        with tag_quote(buffer, "figure"):
            buffer.write(self.dump_blocks(e.blocks))
            if e.caption.short_caption or e.caption.blocks:
                with tag_quote(buffer, "figcaption"):
                    if e.caption.short_caption:
                        buffer.write(self.dump_inlines(e.caption.short_caption.inlines))
                    if e.caption.blocks:
                        buffer.write(self.dump_blocks(e.caption.blocks))
        return buffer.getvalue()

    @override
    def on_header(self, e: Header) -> str:
        assert 1 <= e.level
        buffer = StringIO()
        with tag_quote(buffer, f"h{e.level}"):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_horizontal_rule(self, e: HorizontalRule) -> str:
        return "<hr />\n"

    @override
    def on_line_block(self, e: LineBlock) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nobr
        buffer = StringIO()
        with tag_quote(buffer, "span", style="white-space:nowrap"):
            for inlines in e.inliness:
                buffer.write(self.dump_inlines(inlines))
        return buffer.getvalue()

    @override
    def on_ordered_list(self, e: OrderedList) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "ol", start=e.list_attributes.start_number):
            for blocks in e.blockss:
                with tag_quote(buffer, "li"):
                    buffer.write(self.dump_blocks(blocks))
        return buffer.getvalue()

    @override
    def on_para(self, e: Para) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "p"):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_plain(self, e: Plain) -> str:
        return self.dump_inlines(e.inlines)

    @override
    def on_raw_block(self, e: RawBlock) -> str:
        if e.format == "html":
            lower_text = e.text.lower()
            if lower_text in self._references_tags:
                return self.on_references()
            elif lower_text in self._convert_raw_tags:
                return self._convert_raw_tags[lower_text]
            elif lower_text.startswith("<div ") and lower_text.endswith(">"):
                return e.text
            elif lower_text.startswith("<references ") and lower_text.endswith("/>"):
                return str()  # e.g. '<references group="nb" />' in 'ANSI_escape_code'
            else:
                # raise ValueError(f"Unsupported html text: '{e.text}'")
                return e.text.replace("<", "&lt;").replace(">", "&gt;")
        elif e.format == "mediawiki":
            # return e.text  # e.g. {{{ ... }}}
            # raise ValueError(f"Unsupported mediawiki text: '{e.text}'")
            return e.text.replace("{", "&#123;").replace("}", "&#125;")
        else:
            raise ValueError(f"Unsupported RawBlock's format: '{e.format}'")

    def on_cell(self, e: Cell) -> str:
        kwargs: Dict[str, Any] = dict()
        kwargs.update(e.attr.kwargs)

        match e.alignment:
            case Alignment.AlignLeft:
                kwargs["align"] = "left"
            case Alignment.AlignRight:
                kwargs["align"] = "right"
            case Alignment.AlignCenter:
                kwargs["align"] = "center"
            case Alignment.AlignDefault:
                pass
            case _:
                raise ValueError(f"Invalid alignment value: {e.alignment}")

        if 1 <= e.row_span:
            kwargs["rowspan"] = e.row_span

        if 1 <= e.col_span:
            kwargs["colspan"] = e.col_span

        buffer = StringIO()
        with tag_quote(buffer, "td", **kwargs):
            buffer.write(self.dump_blocks(e.blocks))
        return buffer.getvalue()

    def on_row(self, e: Row) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError

        buffer = StringIO()
        with tag_quote(buffer, "tr"):
            for cell in e.cells:
                buffer.write(self.on_cell(cell))
        return buffer.getvalue()

    @override
    def on_table(self, e: Table) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError

        buffer = StringIO()
        with tag_quote(buffer, "table"):
            if e.caption.short_caption or e.caption.blocks:
                with tag_quote(buffer, "caption"):
                    if e.caption.short_caption:
                        buffer.write(self.dump_inlines(e.caption.short_caption.inlines))
                    if e.caption.blocks:
                        buffer.write(self.dump_blocks(e.caption.blocks))

            if e.table_head:
                with tag_quote(buffer, "thead"):
                    if not e.table_head.attr.is_empty:
                        raise NotImplementedError
                    for row in e.table_head.rows:
                        buffer.write(self.on_row(row))

            for tbody in e.table_body:
                with tag_quote(buffer, "tbody"):
                    if not tbody.attr.is_empty:
                        raise NotImplementedError
                    # row_head_columns = tbody.row_head_columns  # TODO
                    for row in tbody.header_rows:
                        buffer.write(self.on_row(row))
                    for row in tbody.body_rows:
                        buffer.write(self.on_row(row))

            if e.table_foot:
                with tag_quote(buffer, "tfoot"):
                    if not e.table_foot.attr.is_empty:
                        raise NotImplementedError
                    for row in e.table_foot.rows:
                        buffer.write(self.on_row(row))

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
        # citations = e.citations  # TODO
        buffer = StringIO()
        with tag_quote(buffer, "cite", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_code(self, e: Code) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        buffer.write("`")
        buffer.write(e.text.replace("`", "&#96;"))
        buffer.write("`")
        return buffer.getvalue()

    @override
    def on_emph(self, e: Emph) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "em", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_image(self, e: Image) -> str:
        if not self._no_skip_attachments:
            return self.dump_inlines(e.inlines)

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
        text = self.dump_inlines(e.inlines)
        try:
            link = e.target.as_markdown_link(
                no_extension=self._no_extension,
                no_abspath=self._no_abspath,
                filenames=self._filenames,
            )
            buffer.write(f"[{text}]({link})")
        except FileNotFoundError:
            with tag_quote(buffer, "span", newline=None):
                buffer.write(text)
        finally:
            return buffer.getvalue()

    @override
    def on_math(self, e: Math) -> str:
        if e.math_type == MathType.DisplayMath:
            return f"$$\n{e.text.strip()}\n$$\n"
        else:
            assert e.math_type == MathType.InlineMath
            return f"${e.text.strip()}$"

    @override
    def on_note(self, e: Note) -> str:
        index = len(self._footnotes)
        self._footnotes.append(e)
        return f"[^{index}]"

    @override
    def on_quoted(self, e: Quoted) -> str:
        # quote_type = e.quote_type  # TODO
        buffer = StringIO()
        with tag_quote(buffer, "q", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_raw_inline(self, e: RawInline) -> str:
        if e.format == "html":
            lower_text = e.text.lower()
            if lower_text in self._convert_raw_tags:
                return self._convert_raw_tags[lower_text]
            else:
                # raise ValueError(f"Unsupported html text: '{e.text}'")
                return e.text.replace("<", "&lt;").replace(">", "&gt;")
        elif e.format == "mediawiki":
            # return e.text  # e.g. {{{ ... }}}
            # raise ValueError(f"Unsupported mediawiki text: '{e.text}'")
            return e.text.replace("{", "&#123;").replace("}", "&#125;")
        else:
            raise ValueError(f"Unsupported RawBlock's format: {e.format}")

    @override
    def on_small_caps(self, e: SmallCaps) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "small", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_soft_break(self, e: SoftBreak) -> str:
        return "\n"

    @override
    def on_space(self, e: Space) -> str:
        return " "  # "&nbsp;"

    @override
    def on_span(self, e: Span) -> str:
        if not e.attr.is_empty:
            raise NotImplementedError
        buffer = StringIO()
        with tag_quote(buffer, "span", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_str(self, e: Str) -> str:
        return e.text

    @override
    def on_strikeout(self, e: Strikeout) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "del", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_strong(self, e: Strong) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "strong", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_subscript(self, e: Subscript) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "sub", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_superscript(self, e: Superscript) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "sup", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    @override
    def on_underline(self, e: Underline) -> str:
        buffer = StringIO()
        with tag_quote(buffer, "u", newline=None):
            buffer.write(self.dump_inlines(e.inlines))
        return buffer.getvalue()

    # ----------------------------------------------------------------------------------
    # ETC Events
    # ----------------------------------------------------------------------------------

    def on_references(self) -> str:
        if not self._footnotes:
            return str()

        try:
            buffer = StringIO()
            for i, note in enumerate(self._footnotes):
                buffer.write(f"[^{i}]: ")
                buffer.write(strip_tags(self.dump_blocks(note.blocks)).strip())
                buffer.write("\n")
            return buffer.getvalue()
        finally:
            self._footnotes.clear()
