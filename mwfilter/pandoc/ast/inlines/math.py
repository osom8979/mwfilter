# -*- coding: utf-8 -*-

from dataclasses import dataclass, field

from mwfilter.pandoc.ast.enums import MathType
from mwfilter.pandoc.ast.inlines.inline import Inline
from mwfilter.types.override import override


@dataclass
class Math(Inline):
    """TeX's math (literal)"""

    math_type: MathType = MathType.DisplayMath
    text: str = field(default_factory=str)

    @classmethod
    @override
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 2
        math_type = MathType.parse_object(e[0])
        text = e[1]
        assert isinstance(text, str)
        return cls(math_type, text)
