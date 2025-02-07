# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from dataclasses import dataclass, field
from enum import StrEnum, unique
from json import loads
from typing import Any, Dict, List, Optional, Tuple

from pypandoc import convert_text


@unique
class ListNumberStyle(StrEnum):
    """Style of list numbers."""

    DefaultStyle = "DefaultStyle"
    Example = "Example"
    Decimal = "Decimal"
    LowerRoman = "LowerRoman"
    UpperRoman = "UpperRoman"
    LowerAlpha = "LowerAlpha"
    UpperAlpha = "UpperAlpha"


@unique
class ListNumberDelim(StrEnum):
    """Delimiter of list numbers."""

    DefaultDelim = "DefaultDelim"
    Period = "Period"
    OneParen = "OneParen"
    TwoParens = "TwoParens"


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
        start_number = e[0]
        assert isinstance(start_number, int)

        e_list_number_style = e[1]
        assert isinstance(e_list_number_style, dict)
        list_number_style = ListNumberStyle(e_list_number_style["t"])

        e_list_number_delim = e[2]
        assert isinstance(e_list_number_delim, dict)
        list_number_delim = ListNumberDelim(e_list_number_delim["t"])

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
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Underline(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Strong(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Strikeout(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Superscript(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Subscript(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class SmallCaps(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Quoted(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Cite(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Code(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Space(Inline):
    """Inter-word space"""

    @classmethod
    def parse_object(cls, e):
        assert e is None
        return cls()


@dataclass
class SoftBreak(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class LineBreak(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Math(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class RawInline(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Link(Inline):
    """Hyperlink: alt text (list of inlines), target"""
    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)
    target: Target = field(default_factory=Target)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        attr = Attr.parse_object(e[0])
        inlines = list()
        for e_inline in e[1]:
            inlines.append(parse_inline(e_inline))
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
        attr = Attr.parse_object(e[0])
        inlines = list()
        for e_inline in e[1]:
            inlines.append(parse_inline(e_inline))
        target = Target.parse_object(e[2])
        return cls(attr, inlines, target)


@dataclass
class Note(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Span(Inline):
    @classmethod
    def parse_object(cls, e):
        return cls()


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


class Block:
    pass


@dataclass
class Plain(Block):
    """Plain text, not a paragraph"""
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        inlines = list()
        for e_inline in e:
            inlines.append(parse_inline(e_inline))
        return cls(inlines)


@dataclass
class Para(Block):
    """Paragraph"""
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        inlines = list()
        for e_inline in e:
            inlines.append(parse_inline(e_inline))
        return cls(inlines)


@dataclass
class LineBlock(Block):
    """Multiple non-breaking lines"""
    inliness: List[List[Inline]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        inliness = list()
        for e_inlines in e:
            inlines = list()
            for e_inline in e_inlines:
                inlines.append(parse_inline(e_inline))
            inliness.append(inlines)
        return cls(inliness)


@dataclass
class CodeBlock(Block):
    """Code block (literal) with attributes"""
    attr: Attr = field(default_factory=Attr)
    text: str = field(default_factory=str)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
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
        assert isinstance(e, list)
        blocks = list()
        for e_block in e:
            blocks.append(parse_block(e_block))
        return cls(blocks)


@dataclass
class OrderedList(Block):
    """Ordered list (attributes and a list of items, each a list of blocks)"""
    list_attributes: ListAttributes = field(default_factory=ListAttributes)
    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        list_attributes = ListAttributes.parse_object(e[0])
        blockss = list()
        for e_blocks in e[1]:
            blocks = list()
            for e_block in e_blocks:
                blocks.append(parse_block(e_block))
            blockss.append(blocks)
        return cls(list_attributes, blockss)


@dataclass
class BulletList(Block):
    """Bullet list (list of items, each a list of blocks)"""
    blockss: List[List[Block]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        blockss = list()
        for e_blocks in e:
            blocks = list()
            for e_block in e_blocks:
                blocks.append(parse_block(e_block))
            blockss.append(blocks)
        return cls(blockss)


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
        items = list()
        for e_item in e:
            inlines = list()
            for e_inline in e_item[0]:
                inlines.append(parse_inline(e_inline))

            blockss = list()
            for e_blocks in e_item[1]:
                blocks = list()
                for e_block in e_blocks:
                    blocks.append(parse_block(e_block))
                blockss.append(blocks)

            items.append((inlines, blockss))
        return cls(items)


@dataclass
class Header(Block):
    """Header - level (integer) and text (inlines)"""
    level: int = 0
    attr: Attr = field(default_factory=Attr)
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        level = e[0]
        assert isinstance(level, int)
        attr = Attr.parse_object(e[1])
        inlines = list()
        for e_inline in e[2]:
            inlines.append(parse_inline(e_inline))
        return cls(level, attr, inlines)


@dataclass
class HorizontalRule(Block):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class Table(Block):
    @classmethod
    def parse_object(cls, e):
        return cls()


@dataclass
class ShortCaption:
    """A short caption, for use in, for instance, lists of figures."""
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        inlines = list()
        for e_inline in e:
            inlines.append(parse_inline(e_inline))
        return cls(inlines)


@dataclass
class Caption:
    """The caption of a table or figure, with optional short caption."""
    short_caption: Optional[ShortCaption] = None
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        short_caption = e[0]
        assert isinstance(short_caption, (type(None), list))
        blocks = list()
        for e_block in e[1]:
            blocks.append(parse_block(e_block))
        return cls(short_caption, blocks)


@dataclass
class Figure(Block):
    """Figure, with attributes, caption, and content (list of blocks)"""
    attr: Attr = field(default_factory=Attr)
    caption: Caption = field(default_factory=Caption)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        attr = Attr.parse_object(e[0])
        caption = Caption.parse_object(e[1])
        blocks = list()
        for e_block in e[2]:
            blocks.append(parse_block(e_block))
        return cls(attr, caption, blocks)


@dataclass
class Div(Block):
    @classmethod
    def parse_object(cls, e):
        return cls()


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

    # ----------------------------------------------------------------------------------
    # Block elements.
    # ----------------------------------------------------------------------------------

    def on_horizontal_rule(self, e):
        """Horizontal rule"""
        assert self
        return e

    def on_table(self, e):
        """
        Table, with attributes, caption, optional short caption, column alignments and
        widths (required), table head, table bodies, and table foot
        """
        assert isinstance(e, list)
        self.on_attr(e[0])
        self.on_caption(e[1])
        for col_spec in e[2]:
            self.on_col_spec(col_spec)
        self.on_table_head(e[3])
        for table_body in e[4]:
            self.on_table_body(table_body)
        self.on_table_foot(e[5])
        return e

    def on_caption(self, e):
        """The caption of a table or figure, with optional short caption."""
        assert self
        # (Maybe ShortCaption) [Block]
        return e

    def on_table_head(self, e):
        """The head of a table."""
        assert self
        assert isinstance(e, list)
        self.on_attr(e[0])
        for row in e[1]:
            self.on_row(row)
        return e

    def on_table_foot(self, e):
        assert self
        return e

    def on_div(self, e):
        """Generic block container with attributes"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        for block in e[2]:
            self.on_block(block)
        return e

    # ----------------------------------------------------------------------------------
    # Table elements.
    # ----------------------------------------------------------------------------------

    def on_col_spec(self, e):
        """The specification for a single table column."""
        assert self
        self.on_alignment(e[0])
        col_width = e[1]
        # The width of a table column,
        # as a percentage of the text width.
        assert isinstance(col_width, float)

        return e

    def on_alignment(self, e):
        """Alignment of a table column."""
        assert self
        assert isinstance(e, str)
        # AlignLeft
        # AlignRight
        # AlignCenter
        # AlignDefault
        return e

    def on_table_body(self, e):
        """
        A body of a table, with an intermediate head, intermediate body,
        and the specified number of row header columns in the intermediate body.
        """
        assert isinstance(e, dict)
        self.on_attr(e[0])
        row_head_columns = e[1]
        assert isinstance(row_head_columns, int)
        for row in e[2]:
            self.on_row(row)
        for row in e[3]:
            self.on_row(row)
        assert self
        return e

    def on_row(self, e):
        """A table row."""
        self.on_attr(e[0])
        for cell in e[1]:
            self.on_cell(cell)
        return e

    def on_cell(self, e):
        """A table cell."""
        self.on_attr(e[0])
        self.on_alignment(e[1])
        row_span = e[2]
        col_span = e[3]
        assert isinstance(row_span, int)
        assert isinstance(col_span, int)
        for block in e[4]:
            self.on_block(block)
        return e

    # ----------------------------------------------------------------------------------
    # Inline elements.
    # ----------------------------------------------------------------------------------

    def on_emph(self, e):
        """Emphasized text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_underline(self, e):
        """Underlined text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_strong(self, e):
        """Strongly emphasized text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_strikeout(self, e):
        """Strikeout text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_superscript(self, e):
        """Superscripted text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_subscript(self, e):
        """Subscripted text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_small_caps(self, e):
        """Small caps text (list of inlines)"""
        assert isinstance(e, list)
        for inline in e[0]:
            self.on_inline(inline)
        return e

    def on_quoted(self, e):
        """Quoted text (list of inlines)"""
        assert isinstance(e, list)
        self.on_quote_type(e[0])
        for inline in e[1]:
            self.on_inline(inline)
        return e

    def on_cite(self, e):
        """Citation (list of inlines)"""
        assert isinstance(e, list)
        for citation in e[0]:
            self.on_citation(citation)
        for inline in e[1]:
            self.on_inline(inline)
        return e

    def on_code(self, e):
        """Inline code (literal)"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        text = e[1]
        assert isinstance(text, str)
        return e

    def on_soft_break(self, e):
        """Soft line break"""
        assert self
        return e

    def on_line_break(self, e):
        """Hard line break"""
        assert self
        return e

    def on_math(self, e):
        """TeX's math (literal)"""
        assert isinstance(e, list)
        self.on_math_type(e[0])
        text = e[1]
        assert isinstance(text, str)
        return e

    def on_raw_inline(self, e):
        """Raw inline"""
        assert self
        assert isinstance(e, list)
        format_ = e[0]
        assert isinstance(format_, str)
        text = e[1]
        assert isinstance(text, str)
        return e

    def on_note(self, e):
        """Footnote or endnote"""
        assert isinstance(e, list)
        for block in e[0]:
            self.on_block(block)
        return e

    def on_span(self, e):
        """Generic inline container with attributes"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        for inline in e[1]:
            self.on_inline(inline)

    # ----------------------------------------------------------------------------------
    # Common elements.
    # ----------------------------------------------------------------------------------

    def on_citation(self, e):
        assert self
        return e

    def on_quote_type(self, e):
        """Type of quotation marks to use in Quoted inline."""
        assert self
        # SingleQuote
        # DoubleQuote
        return e

    def on_math_type(self, e):
        """Type of math element (display or inline)."""
        assert self
        # DisplayMath
        # InlineMath
        return e
