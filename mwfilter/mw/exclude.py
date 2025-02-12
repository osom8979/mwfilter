# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from re import match
from typing import List

from mwfilter.pandoc.ast.blocks.bullet_list import BulletList
from mwfilter.pandoc.ast.blocks.plain import Plain
from mwfilter.pandoc.ast.inlines.link import Link
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc


@dataclass
class Exclude:
    pages: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)

    @classmethod
    def from_mediawiki_content(cls, mediawiki_content: str):
        pages: List[str] = list()
        patterns: List[str] = list()

        pandoc = Pandoc.parse_text(mediawiki_content)
        for block in pandoc.blocks:
            if not isinstance(block, BulletList):
                raise TypeError(
                    f"The {type(block).__name__} type is not allowed. "
                    "The root block type must only allow BulletList."
                )

            for bs in block.blockss:
                if 1 != len(bs):
                    raise ValueError(
                        f"Blocks has {len(bs)} child elements. It must have exactly 1."
                    )

                b = bs[0]

                if not isinstance(b, Plain):
                    raise TypeError(
                        f"The {type(b).__name__} type is not allowed. "
                        "The element block type must only allow Plain."
                    )

                if 1 != len(b.inlines):
                    raise ValueError(
                        f"Inlines has {len(b.inlines)} child elements. "
                        "It must have exactly 1."
                    )

                inline = b.inlines[0]

                if isinstance(inline, Link):
                    if inline.target.is_wikilink:
                        pages.append(inline.target.url)
                    else:
                        raise ValueError(f"Unsupported link target: {inline.target}")
                elif isinstance(inline, Str):
                    patterns.append(inline.text)

        return cls(pages=pages, patterns=patterns)

    def filter_with_title(self, title: str) -> bool:
        if self.pages and title in self.pages:
            return False

        if self.patterns:
            for pattern in self.patterns:
                if match(pattern, title) is not None:
                    return False

        return True
