# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from dataclasses import dataclass, field
from json import loads
from typing import Any, Dict, Final, List, Optional, Tuple

from pypandoc import convert_text

from mwfilter.pandoc.ast.attr import Attr
from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.enums import Alignment
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines, parse_inliness
from mwfilter.pandoc.ast.list_attributes import ListAttributes


@dataclass
class Plain(Block):
    """Plain text, not a paragraph"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Para(Block):
    """Paragraph"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class LineBlock(Block):
    """Multiple non-breaking lines"""

    inliness: List[List[Inline]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inliness(e))


@dataclass
class CodeBlock(Block):
    """Code block (literal) with attributes"""

    attr: Attr = field(default_factory=Attr)
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        text = e[1]
        assert isinstance(text, str)
        return cls(attr, text)


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


@dataclass
class BlockQuote(Block):
    """Block quote (list of blocks)"""

    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_blocks(e))


@dataclass
class OrderedList(Block):
    """Ordered list (attributes and a list of items, each a list of blocks)"""

    list_attributes: ListAttributes = field(default_factory=ListAttributes)
    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        list_attributes = ListAttributes.parse_object(e[0])
        blockss = parse_blockss(e[1])
        return cls(list_attributes, blockss)


@dataclass
class BulletList(Block):
    """Bullet list (list of items, each a list of blocks)"""

    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_blockss(e))


@dataclass
class DefinitionList(Block):
    """
    Definition list.
    Each list item is a pair consisting of a term (a list of inlines)
    and one or more definitions (each a list of blocks)
    """

    items: List[Tuple[List[Inline], List[List[Block]]]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        return cls([(parse_inlines(i), parse_blockss(b)) for i, b in e])


@dataclass
class Header(Block):
    """Header - level (integer) and text (inlines)"""

    level: int = 0
    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        level = e[0]
        assert isinstance(level, int)
        attr = Attr.parse_object(e[1])
        inlines = parse_inlines(e[2])
        return cls(level, attr, inlines)


@dataclass
class HorizontalRule(Block):
    """Horizontal rule"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()


@dataclass
class ShortCaption:
    """A short caption, for use in, for instance, lists of figures."""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


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


class ColWidth(float):
    """The width of a table column, as a percentage of the text width."""

    DEFAULT: Final[float] = 0.0

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        if e["t"] == "ColWidthDefault":
            return cls(0.0)
        elif e["t"] == "ColWidth":
            assert isinstance(e["c"], float)
            return cls(e["c"])
        else:
            raise ValueError(f"Unexpected element type: {e}")

    @property
    def is_default(self):
        return self == self.DEFAULT


@dataclass
class ColSpec:
    """The specification for a single table column."""

    alignment: Alignment = Alignment.AlignDefault
    col_width: ColWidth = field(default_factory=ColWidth)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        alignment = Alignment.parse_object(e[0])
        col_width = ColWidth.parse_object(e[1])
        return cls(alignment, col_width)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)


class RowSpan(int):
    """The number of rows occupied by a cell; the height of a cell."""

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)


class ColSpan(int):
    """The number of columns occupied by a cell; the width of a cell."""

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)


@dataclass
class Cell:
    """A table cell."""

    attr: Attr = field(default_factory=Attr)
    alignment: Alignment = Alignment.AlignDefault
    row_span: RowSpan = field(default_factory=RowSpan)
    col_span: ColSpan = field(default_factory=ColSpan)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 5
        attr = Attr.parse_object(e[0])
        alignment = Alignment.parse_object(e[1])
        row_span = RowSpan.parse_object(e[2])
        col_span = ColSpan.parse_object(e[3])
        blocks = parse_blocks(e[4])
        return cls(attr, alignment, row_span, col_span, blocks)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)


@dataclass
class Row:
    """A table row."""

    attr: Attr = field(default_factory=Attr)
    cells: List[Cell] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        cells = Cell.parse_object_with_list(e[1])
        return cls(attr, cells)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)


@dataclass
class TableHead:
    """The head of a table."""

    attr: Attr = field(default_factory=Attr)
    rows: List[Row] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        rows = Row.parse_object_with_list(e[1])
        return cls(attr, rows)


class RowHeadColumns(int):
    """
    The number of columns taken up by the row head of each row of a TableBody.
    The row body takes up the remaining columns.
    """

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)


@dataclass
class TableBody:
    """
    A body of a table, with an intermediate head, intermediate body,
    and the specified number of row header columns in the intermediate body.

    Warning:
        The <thead>, <tbody>, <tfoot>, <colgroup>, and <col> elements are currently not
        supported in MediaWiki
    """

    attr: Attr = field(default_factory=Attr)
    row_head_columns: RowHeadColumns = field(default_factory=RowHeadColumns)
    header_rows: List[Row] = field(default_factory=list)
    body_rows: List[Row] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 4
        attr = Attr.parse_object(e[0])
        row_head_columns = RowHeadColumns.parse_object(e[1])
        header_rows = Row.parse_object_with_list(e[2])
        body_rows = Row.parse_object_with_list(e[3])
        return cls(attr, row_head_columns, header_rows, body_rows)

    @classmethod
    def parse_object_with_list(cls, e):
        assert isinstance(e, list)
        return list(cls.parse_object(item) for item in e)


@dataclass
class TableFoot:
    """The foot of a table."""

    attr: Attr = field(default_factory=Attr)
    rows: List[Row] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        rows = Row.parse_object_with_list(e[1])
        return cls(attr, rows)


@dataclass
class Table(Block):
    """
    Table, with attributes, caption, optional short caption, column alignments and
    widths (required), table head, table bodies, and table foot
    """

    attr: Attr = field(default_factory=Attr)
    caption: Caption = field(default_factory=Caption)
    col_specs: List[ColSpec] = field(default_factory=list)
    table_head: TableHead = field(default_factory=TableHead)
    table_body: List[TableBody] = field(default_factory=list)
    table_foot: TableFoot = field(default_factory=TableFoot)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 6
        attr = Attr.parse_object(e[0])
        caption = Caption.parse_object(e[1])
        col_specs = ColSpec.parse_object_with_list(e[2])
        table_head = TableHead.parse_object(e[3])
        table_body = TableBody.parse_object_with_list(e[4])
        table_foot = TableFoot.parse_object(e[5])
        return cls(attr, caption, col_specs, table_head, table_body, table_foot)


@dataclass
class Figure(Block):
    """Figure, with attributes, caption, and content (list of blocks)"""

    attr: Attr = field(default_factory=Attr)
    caption: Caption = field(default_factory=Caption)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        attr = Attr.parse_object(e[0])
        caption = Caption.parse_object(e[1])
        blocks = parse_blocks(e[2])
        return cls(attr, caption, blocks)


@dataclass
class Div(Block):
    """Generic block container with attributes"""

    attr: Attr = field(default_factory=Attr)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        blocks = parse_blocks(e[1])
        return cls(attr, blocks)


def parse_block(e) -> Block:
    assert isinstance(e, dict)
    e_type = e.get("t")
    e_content = e.get("c")
    assert isinstance(e_type, str)
    match e_type:
        case Plain.__name__:
            return Plain.parse_object(e_content)
        case Para.__name__:
            return Para.parse_object(e_content)
        case LineBlock.__name__:
            return LineBlock.parse_object(e_content)
        case CodeBlock.__name__:
            return CodeBlock.parse_object(e_content)
        case RawBlock.__name__:
            return RawBlock.parse_object(e_content)
        case BlockQuote.__name__:
            return BlockQuote.parse_object(e_content)
        case OrderedList.__name__:
            return OrderedList.parse_object(e_content)
        case BulletList.__name__:
            return BulletList.parse_object(e_content)
        case DefinitionList.__name__:
            return DefinitionList.parse_object(e_content)
        case Header.__name__:
            return Header.parse_object(e_content)
        case HorizontalRule.__name__:
            return HorizontalRule.parse_object(e_content)
        case Table.__name__:
            return Table.parse_object(e_content)
        case Figure.__name__:
            return Figure.parse_object(e_content)
        case Div.__name__:
            return Div.parse_object(e_content)
        case _:
            raise ValueError(f"Unexpected block type: {e_type}")


def parse_blocks(e):
    assert isinstance(e, list)
    return list(parse_block(item) for item in e)


def parse_blockss(e):
    assert isinstance(e, list)
    return list(parse_blocks(item) for item in e)


@dataclass
class Pandoc:
    pandoc_api_version: Tuple[int, int, int] = 0, 0, 0
    meta: Dict[str, Any] = field(default_factory=dict)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_text(cls, content: str, content_format="mediawiki"):
        json_text = convert_text(content, to="json", format=content_format)
        return cls.parse_object(loads(json_text))

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)

        if e_pandoc_api_version := e.get("pandoc-api-version"):
            assert isinstance(e_pandoc_api_version, list)
            assert len(e_pandoc_api_version) == 3
            major, minor, patch = e_pandoc_api_version
            assert isinstance(major, int)
            assert isinstance(minor, int)
            assert isinstance(patch, int)
            pandoc_api_version = major, minor, patch
        else:
            pandoc_api_version = 0, 0, 0

        if e_meta := e.get("meta"):
            assert isinstance(e_meta, dict)
            meta = e_meta.copy()
        else:
            meta = dict()

        blocks = list()
        if e_blocks := e.get("blocks"):
            assert isinstance(e_blocks, list)
            for block in e_blocks:
                assert isinstance(block, dict)
                blocks.append(parse_block(block))

        return cls(pandoc_api_version, meta, blocks)
