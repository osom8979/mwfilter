# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Dict, Sequence, Type

from mwfilter.pandoc.ast.inlines.inline import Inline


@lru_cache
def inline_classes() -> Sequence[Type[Inline]]:
    # [IMPORTANT] Avoid 'circular import' issues
    from mwfilter.pandoc.ast.inlines.cite import Cite
    from mwfilter.pandoc.ast.inlines.code import Code
    from mwfilter.pandoc.ast.inlines.emph import Emph
    from mwfilter.pandoc.ast.inlines.image import Image
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

    return (
        Cite,
        Code,
        Emph,
        Image,
        LineBreak,
        Link,
        Math,
        Note,
        Quoted,
        RawInline,
        SmallCaps,
        SoftBreak,
        Space,
        Span,
        Str,
        Strikeout,
        Strong,
        Subscript,
        Superscript,
        Underline,
    )


@lru_cache
def inline_map() -> Dict[str, Type[Inline]]:
    return {cls.__name__: cls for cls in inline_classes()}


def parse_inline(e) -> Inline:
    assert isinstance(e, dict)
    e_type = e.get("t")
    e_content = e.get("c")
    assert isinstance(e_type, str)
    return inline_map()[e_type].parse_object(e_content)


def parse_inlines(e):
    assert isinstance(e, list)
    return list(parse_inline(item) for item in e)


def parse_inliness(e):
    assert isinstance(e, list)
    return list(parse_inlines(item) for item in e)
