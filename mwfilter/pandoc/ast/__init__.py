# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from dataclasses import dataclass, field
from json import loads
from typing import Any, Dict, Final, List, Optional, Tuple

from pypandoc import convert_text

from mwfilter.pandoc.ast.enums import (
    Alignment,
    ListNumberDelim,
    ListNumberStyle,
    MathType,
    QuoteType,
)


class Meta(Dict[str, Any]):
    pass


@dataclass
class ListAttributes:
    """
    List attributes.
    The first element of the triple is the start number of the list.
    """

    start_number: int = 0
    list_number_style: ListNumberStyle = ListNumberStyle.DefaultStyle
    list_number_delim: ListNumberDelim = ListNumberDelim.DefaultDelim

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        start_number = e[0]
        assert isinstance(start_number, int)
        list_number_style = ListNumberStyle.parse_object(e[1])
        list_number_delim = ListNumberDelim.parse_object(e[2])
        return cls(start_number, list_number_style, list_number_delim)


@dataclass
class Target:
    """Link target (URL, title)."""

    url: str = field(default_factory=str)
    title: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        url = e[0]
        title = e[1]
        assert isinstance(url, str)
        assert isinstance(title, str)
        return cls(url, title)

    @property
    def is_wikilink(self):
        return self.title == "wikilink"


@dataclass
class Attr:
    """Attributes: identifier, classes, key-value pairs"""

    identifier: str = field(default_factory=str)
    classes: List[str] = field(default_factory=list)
    pairs: List[Tuple[str, str]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)

        identifier = e[0]
        assert isinstance(identifier, str)

        classes = list()
        for e_class in e[1]:
            assert isinstance(e_class, str)
            classes.append(e_class)

        pairs = list()
        for e_pair in e[2]:
            key = e_pair[0]
            value = e_pair[1]
            assert isinstance(key, str)
            assert isinstance(value, str)
            pairs.append((key, value))

        return cls(identifier, classes, pairs)

    @property
    def is_empty(self):
        return not self.identifier and not self.classes and not self.pairs


class Inline:
    pass


@dataclass
class Str(Inline):
    """Text (string)"""

    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, str)
        return cls(e)


@dataclass
class Emph(Inline):
    """Emphasized text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Underline(Inline):
    """Underlined text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Strong(Inline):
    """Strongly emphasized text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Strikeout(Inline):
    """Strikeout text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Superscript(Inline):
    """Superscripted text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Subscript(Inline):
    """Subscripted text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class SmallCaps(Inline):
    """Small caps text (list of inlines)"""

    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        return cls(parse_inlines(e))


@dataclass
class Quoted(Inline):
    """Quoted text (list of inlines)"""

    quote_type: QuoteType = QuoteType.SingleQuote
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        quote_type = QuoteType.parse_object(e[0])
        inlines = parse_inlines(e[1])
        return cls(quote_type, inlines)


@dataclass
class Citation:
    # id_: str
    # prefix: List[Inline]
    # suffix: List[Inline]
    # mode: CitationMode
    # notenum: int
    # hash: int

    @classmethod
    def parse_object(cls, e):
        return cls()

    @classmethod
    def parse_object_with_list(cls, e):
        return list(cls.parse_object(item) for item in e)


@dataclass
class Cite(Inline):
    """Citation (list of inlines)"""

    citations: List[Citation] = field(default_factory=list)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        citations = Citation.parse_object_with_list(e[0])
        inlines = parse_inlines(e[1])
        return cls(citations, inlines)


@dataclass
class Code(Inline):
    """Inline code (literal)"""

    attr: Attr = field(default_factory=Attr)
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        text = e[1]
        return cls(attr, text)


@dataclass
class Space(Inline):
    """Inter-word space"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()


@dataclass
class SoftBreak(Inline):
    """Soft line break"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()


@dataclass
class LineBreak(Inline):
    """Hard line break"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()


@dataclass
class Math(Inline):
    """TeX's math (literal)"""

    math_type: MathType = MathType.DisplayMath
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        math_type = MathType.parse_object(e[0])
        text = e[1]
        assert isinstance(text, str)
        return cls(math_type, text)


@dataclass
class RawInline(Inline):
    """Raw inline"""

    format: str = field(default_factory=str)
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        format_ = e[0]
        assert isinstance(format_, str)
        text = e[1]
        assert isinstance(text, str)
        return cls(format_, text)


@dataclass
class Link(Inline):
    """Hyperlink: alt text (list of inlines), target"""

    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)
    target: Target = field(default_factory=Target)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        attr = Attr.parse_object(e[0])
        inlines = parse_inlines(e[1])
        target = Target.parse_object(e[2])
        return cls(attr, inlines, target)


@dataclass
class Image(Inline):
    """Image: alt text (list of inlines), target"""

    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)
    target: Target = field(default_factory=Target)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        attr = Attr.parse_object(e[0])
        inlines = parse_inlines(e[1])
        target = Target.parse_object(e[2])
        return cls(attr, inlines, target)


@dataclass
class Note(Inline):
    """Footnote or endnote"""

    blocks: List["Block"] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        return cls(parse_blocks(e))


@dataclass
class Span(Inline):
    """Generic inline container with attributes"""

    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        attr = Attr.parse_object(e[0])
        inlines = parse_inlines(e[1])
        return cls(attr, inlines)


def parse_inline(e) -> Inline:
    assert isinstance(e, dict)
    e_type = e.get("t")
    e_content = e.get("c")
    assert isinstance(e_type, str)
    match e_type:
        case Str.__name__:
            return Str.parse_object(e_content)
        case Emph.__name__:
            return Emph.parse_object(e_content)
        case Underline.__name__:
            return Underline.parse_object(e_content)
        case Strong.__name__:
            return Strong.parse_object(e_content)
        case Strikeout.__name__:
            return Strikeout.parse_object(e_content)
        case Superscript.__name__:
            return Superscript.parse_object(e_content)
        case Subscript.__name__:
            return Subscript.parse_object(e_content)
        case SmallCaps.__name__:
            return SmallCaps.parse_object(e_content)
        case Quoted.__name__:
            return Quoted.parse_object(e_content)
        case Cite.__name__:
            return Cite.parse_object(e_content)
        case Code.__name__:
            return Code.parse_object(e_content)
        case Space.__name__:
            return Space.parse_object(e_content)
        case SoftBreak.__name__:
            return SoftBreak.parse_object(e_content)
        case LineBreak.__name__:
            return LineBreak.parse_object(e_content)
        case Math.__name__:
            return Math.parse_object(e_content)
        case RawInline.__name__:
            return RawInline.parse_object(e_content)
        case Link.__name__:
            return Link.parse_object(e_content)
        case Image.__name__:
            return Image.parse_object(e_content)
        case Note.__name__:
            return Note.parse_object(e_content)
        case Span.__name__:
            return Span.parse_object(e_content)
        case _:
            raise ValueError(f"Unexpected inline type: {e_type}")


def parse_inlines(e):
    assert isinstance(e, list)
    return list(parse_inline(item) for item in e)


def parse_inliness(e):
    assert isinstance(e, list)
    return list(parse_inlines(item) for item in e)


class Block:
    pass


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
    meta: Meta = field(default_factory=Meta)
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
            meta = Meta(e_meta)
        else:
            meta = Meta()

        blocks = list()
        if e_blocks := e.get("blocks"):
            assert isinstance(e_blocks, list)
            for block in e_blocks:
                assert isinstance(block, dict)
                blocks.append(parse_block(block))

        return cls(pandoc_api_version, meta, blocks)
