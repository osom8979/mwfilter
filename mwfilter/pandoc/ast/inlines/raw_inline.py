# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.types.override import override


@dataclass
class RawInline(Inline):
    """Raw inline"""

    format: str = field(default_factory=str)
    text: str = field(default_factory=str)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        format_ = e[0]
        assert isinstance(format_, str)
        text = e[1]
        assert isinstance(text, str)
        return cls(format_, text)
