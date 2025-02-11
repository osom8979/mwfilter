# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.enums import QuoteType
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.pandoc.ast.inlines.parser import parse_inlines
from mwfilter.types.override import override


@dataclass
class Quoted(Inline):
    """Quoted text (list of inlines)"""

    quote_type: QuoteType = QuoteType.SingleQuote
    inlines: List[Inline] = field(default_factory=list)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        quote_type = QuoteType.parse_object(e[0])
        inlines = parse_inlines(e[1])
        return cls(quote_type, inlines)
