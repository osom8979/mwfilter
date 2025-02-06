# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from typing import Any, Dict, List, Optional, Tuple


class PandocAstParser:
    def __init__(
        self,
        version: Optional[Tuple[int, int, int]] = None,
        meta: Optional[Dict[str, Any]] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
    ):
        self._version = version if version else (0, 0, 0)
        self._meta = {k: v for k, v in (meta if meta else dict()).items()}
        self._blocks = list(blocks if blocks else list())

    @property
    def version(self):
        return self._version

    @property
    def meta(self):
        return self._meta

    @property
    def title(self):
        return self._meta.get("title")

    @property
    def authors(self):
        return self._meta.get("authors")

    @property
    def date(self):
        return self._meta.get("date")

    @property
    def blocks(self):
        return self._blocks

    def on_root(self, e):
        assert isinstance(e, dict)

        if pandoc_api_version := e.get("pandoc-api-version"):
            assert isinstance(pandoc_api_version, list)
            assert len(pandoc_api_version) == 3
            major, minor, patch = pandoc_api_version
            assert isinstance(major, int)
            assert isinstance(minor, int)
            assert isinstance(patch, int)
            self._version = major, minor, patch
        else:
            self._version = 0, 0, 0

        if meta := e.get("meta"):
            assert isinstance(meta, dict)
            self._meta = meta
        else:
            self._meta = dict()

        if blocks := e.get("blocks"):
            assert isinstance(blocks, list)
            result_blocks = list()
            for block in blocks:
                assert isinstance(block, dict)
                result_blocks.append(self.on_block(block))
            self._blocks = result_blocks
        else:
            self._blocks = list()

    # ----------------------------------------------------------------------------------
    # Block elements.
    # ----------------------------------------------------------------------------------

    def on_block(self, e):
        assert isinstance(e, dict)
        e_type = e["t"]
        e_content = e["c"]
        assert isinstance(e_type, str)
        match e_type:
            case "Plain":
                self.on_plain(e_content)
            case "Para":
                self.on_para(e_content)
            case "LineBlock":
                self.on_line_block(e_content)
            case "CodeBlock":
                self.on_code_block(e_content)
            case "RawBlock":
                self.on_raw_block(e_content)
            case "BlockQuote":
                self.on_block_quote(e_content)
            case "OrderedList":
                self.on_ordered_list(e_content)
            case "BulletList":
                self.on_bullet_list(e_content)
            case "DefinitionList":
                self.on_definition_list(e_content)
            case "Header":
                self.on_header(e_content)
            case "HorizontalRule":
                self.on_horizontal_rule(e_content)
            case "Table":
                self.on_table(e_content)
            case "Figure":
                self.on_figure(e_content)
            case "Div":
                self.on_div(e_content)
            case _:
                raise ValueError(f"Unexpected block type: {e_type}")
        return e

    def on_plain(self, e):
        """Plain text, not a paragraph"""
        assert isinstance(e, list)
        for inline in e:
            self.on_inline(inline)
        return e

    def on_para(self, e):
        """Paragraph"""
        assert isinstance(e, list)
        for inline in e:
            self.on_inline(inline)
        return e

    def on_line_block(self, e):
        """Multiple non-breaking lines"""
        assert isinstance(e, list)
        for inlines in e:
            for inline in inlines:
                self.on_inline(inline)
        return e

    def on_code_block(self, e):
        """Code block (literal) with attributes"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        text = e[1]
        assert isinstance(text, str)
        return e

    def on_raw_block(self, e):
        """Raw block"""
        assert self
        assert isinstance(e, list)
        format_ = e[0]
        assert isinstance(format_, str)
        text = e[1]
        assert isinstance(text, str)
        return e

    def on_block_quote(self, e):
        """Block quote (list of blocks)"""
        assert isinstance(e, list)
        for block in e:
            self.on_block(block)
        return e

    def on_ordered_list(self, e):
        """Ordered list (attributes and a list of items, each a list of blocks)"""
        assert isinstance(e, list)
        self.on_list_attributes(e[0])
        for blocks in e[1]:
            for block in blocks:
                self.on_block(block)
        return e

    def on_list_attributes(self, e):
        """
        List attributes.
        The first element of the triple is the start number of the list.
        """
        assert self
        assert isinstance(e, list)
        start_number = e[0]
        assert isinstance(start_number, int)

        list_number_style = e[1]  # Style of list numbers.
        assert isinstance(list_number_style, int)
        # DefaultStyle
        # Example
        # Decimal
        # LowerRoman
        # UpperRoman
        # LowerAlpha
        # UpperAlpha

        list_number_delim = e[2]  # Delimiter of list numbers.
        assert isinstance(list_number_delim, int)
        # DefaultDelim
        # Period
        # OneParen
        # TwoParens
        return e

    def on_bullet_list(self, e):
        """Bullet list (list of items, each a list of blocks)"""
        assert isinstance(e, list)
        for blocks in e[1]:
            for block in blocks:
                self.on_block(block)
        return e

    def on_definition_list(self, e):
        """
        Definition list.
        Each list item is a pair consisting of a term (a list of inlines)
        and one or more definitions (each a list of blocks)
        """
        assert isinstance(e, list)
        for pair in e:
            for inline in pair[0]:
                self.on_inline(inline)
            for blocks in pair[1]:
                for block in blocks:
                    self.on_block(block)
        return e

    def on_header(self, e):
        """Header - level (integer) and text (inlines)"""
        assert isinstance(e, list)
        level = e[0]
        assert isinstance(level, int)
        self.on_attr(e[1])
        for inline in e[2]:
            self.on_inline(inline)
        return e

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

    def on_figure(self, e):
        """Figure, with attributes, caption, and content (list of blocks)"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        self.on_caption(e[1])
        for block in e[2]:
            self.on_block(block)
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

    def on_inline(self, e):
        assert isinstance(e, dict)
        e_type = e["t"]
        e_content = e["c"]
        assert isinstance(e_type, str)
        match e_type:
            case "Str":
                self.on_str(e_content)
            case "Emph":
                self.on_emph(e_content)
            case "Underline":
                self.on_underline(e_content)
            case "Strong":
                self.on_strong(e_content)
            case "Strikeout":
                self.on_strikeout(e_content)
            case "Superscript":
                self.on_superscript(e_content)
            case "Subscript":
                self.on_subscript(e_content)
            case "SmallCaps":
                self.on_small_caps(e_content)
            case "Quoted":
                self.on_quoted(e_content)
            case "Cite":
                self.on_cite(e_content)
            case "Code":
                self.on_code(e_content)
            case "Space":
                self.on_space(e_content)
            case "SoftBreak":
                self.on_soft_break(e_content)
            case "LineBreak":
                self.on_line_break(e_content)
            case "Math":
                self.on_math(e_content)
            case "RawInline":
                self.on_raw_inline(e_content)
            case "Link":
                self.on_link(e_content)
            case "Image":
                self.on_image(e_content)
            case "Note":
                self.on_note(e_content)
            case "Span":
                self.on_span(e_content)
            case _:
                raise ValueError(f"Unexpected inline type: {e_type}")
        return e

    def on_str(self, e):
        """Text (string)"""
        assert self
        assert isinstance(e, list)
        text = e[0]
        assert isinstance(text, str)
        return e

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

    def on_space(self, e):
        """Inter-word space"""
        assert self
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

    def on_link(self, e):
        """Hyperlink: alt text (list of inlines), target"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        for inline in e[1]:
            self.on_inline(inline)
        self.on_target(e[2])
        return e

    def on_image(self, e):
        """Image: alt text (list of inlines), target"""
        assert isinstance(e, list)
        self.on_attr(e[0])
        for inline in e[1]:
            self.on_inline(inline)
        self.on_target(e[2])
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

    def on_attr(self, e):
        """Attributes: identifier, classes, key-value pairs"""
        assert self
        assert isinstance(e, list)
        identifier = e[0]
        assert isinstance(identifier, str)
        for cls in e[1]:
            assert isinstance(cls, str)
        for pair in e[2]:
            key = pair[0]
            value = pair[1]
            assert isinstance(key, str)
            assert isinstance(value, str)
        return e

    def on_target(self, e):
        """Link target (URL, title)."""
        assert self
        assert isinstance(e, list)
        url = e[0]
        title = e[1]
        assert isinstance(url, str)
        assert isinstance(title, str)
        return e

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
