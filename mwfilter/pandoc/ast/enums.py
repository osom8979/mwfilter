# -*- coding: utf-8 -*-

from enum import StrEnum, unique


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

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])


@unique
class ListNumberDelim(StrEnum):
    """Delimiter of list numbers."""

    DefaultDelim = "DefaultDelim"
    Period = "Period"
    OneParen = "OneParen"
    TwoParens = "TwoParens"

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])


@unique
class Alignment(StrEnum):
    """Alignment of a table column."""

    AlignLeft = "AlignLeft"
    AlignRight = "AlignRight"
    AlignCenter = "AlignCenter"
    AlignDefault = "AlignDefault"

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])


@unique
class QuoteType(StrEnum):
    """Type of quotation marks to use in Quoted inline."""

    SingleQuote = "SingleQuote"
    DoubleQuote = "DoubleQuote"

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])


@unique
class CitationMode(StrEnum):
    AuthorInText = "AuthorInText"
    SuppressAuthor = "SuppressAuthor"
    NormalCitation = "NormalCitation"

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])


@unique
class MathType(StrEnum):
    """Type of math element (display or inline)."""

    DisplayMath = "DisplayMath"
    InlineMath = "InlineMath"

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        return cls(e["t"])
