# -*- coding: utf-8 -*-
# https://hackage.haskell.org/package/pandoc-types-1.23.1/docs/Text-Pandoc-Definition.html

from dataclasses import dataclass, field
from json import loads
from typing import Any, Dict, List, Tuple

from pypandoc import convert_text

from mwfilter.pandoc.ast.blocks.block import Block
from mwfilter.pandoc.ast.blocks.parser import parse_blocks


@dataclass
class Pandoc:
    pandoc_api_version: Tuple[int, int, int] = 0, 0, 0
    meta: Dict[str, Any] = field(default_factory=dict)
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
            meta = e_meta.copy()
        else:
            meta = dict()

        if e_blocks := e.get("blocks"):
            blocks = parse_blocks(e_blocks)
        else:
            blocks = list()

        return cls(pandoc_api_version, meta, blocks)
