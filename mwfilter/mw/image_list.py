# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List

from mwfilter.pandoc.ast.blocks.bullet_list import BulletList
from mwfilter.pandoc.ast.blocks.plain import Plain
from mwfilter.pandoc.ast.inlines.link import Link
from mwfilter.pandoc.ast.inlines.str_ import Str
from mwfilter.pandoc.ast.pandoc import Pandoc

FILE_NAMESPACE_PREFIX = "File:"
MEDIA_NAMESPACE_PREFIX = "Media:"


def strip_namespace_prefix(name: str) -> str:
    if name.startswith(FILE_NAMESPACE_PREFIX):
        return name[len(FILE_NAMESPACE_PREFIX) :]
    if name.startswith(MEDIA_NAMESPACE_PREFIX):
        return name[len(MEDIA_NAMESPACE_PREFIX) :]
    return name


@dataclass
class ImageList:
    images: List[str] = field(default_factory=list)

    @classmethod
    def from_mediawiki_content(cls, mediawiki_content: str):
        images: List[str] = list()

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
                    images.append(strip_namespace_prefix(inline.target.url))
                elif isinstance(inline, Str):
                    images.append(strip_namespace_prefix(inline.text))

        return cls(images=images)
