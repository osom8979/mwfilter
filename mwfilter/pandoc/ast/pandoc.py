# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from dataclasses import dataclass, field
from json import loads
from typing import List, Tuple

from pypandoc import convert_text

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks
from mwfilter.pandoc.ast.metas.meta import Meta
from mwfilter.pandoc.ast.validator.mediawiki import mediawiki_validator


@dataclass
class Pandoc:
    pandoc_api_version: Tuple[int, int, int] = 0, 0, 0
    meta: Meta = field(default_factory=Meta)
    blocks: List[Block] = field(default_factory=list)

    @classmethod
    def parse_text(cls, content: str, content_format="mediawiki"):
        json_text = convert_text(content, to="json", format=content_format)
        json_obj = loads(json_text)
        if content_format == "mediawiki":
            mediawiki_validator(json_obj)
        return cls.parse_object(json_obj)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)

        if e_pandoc_api_version := e.get("pandoc-api-version"):
            assert isinstance(e_pandoc_api_version, list)
            major = e_pandoc_api_version[0] if 1 <= len(e_pandoc_api_version) else 0
            minor = e_pandoc_api_version[1] if 2 <= len(e_pandoc_api_version) else 0
            patch = e_pandoc_api_version[2] if 3 <= len(e_pandoc_api_version) else 0
            assert isinstance(major, int)
            assert isinstance(minor, int)
            assert isinstance(patch, int)
            pandoc_api_version = major, minor, patch
        else:
            pandoc_api_version = 0, 0, 0

        if e_meta := e.get("meta"):
            meta = Meta.parse_object(e_meta)
        else:
            meta = Meta()

        if e_blocks := e.get("blocks"):
            blocks = parse_blocks(e_blocks)
        else:
            blocks = list()

        return cls(pandoc_api_version, meta, blocks)
