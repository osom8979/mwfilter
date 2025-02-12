# -*- coding: utf-8 -*-

import json
from dataclasses import dataclass, field
from io import StringIO
from re import match
from typing import List, Optional

from pypandoc import convert_text

from mwfilter.pandoc.ast.pandoc import Pandoc


@dataclass
class Exclude:
    pages: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)

    @classmethod
    def from_mediawiki_content(cls, mediawiki_content: str):
        pandoc = Pandoc.parse_text(mediawiki_content)
        assert pandoc.blocks

        info_json = convert_text(mediawiki_content, to="json", format="mediawiki")
        info_obj = json.loads(info_json)
        assert isinstance(info_obj, dict)
        blocks = info_obj["blocks"]
        assert isinstance(blocks, list)

        pages: List[str] = list()
        patterns: List[str] = list()

        option_cursor: Optional[List[str]] = None

        for block in blocks:
            assert isinstance(block, dict)
            t = block["t"]
            c = block["c"]
            assert isinstance(t, str)
            assert isinstance(c, list)
            if t == "Header":
                header_keyname = c[1][0]
                assert isinstance(header_keyname, str)
                assert header_keyname.islower()
                match header_keyname:
                    case "denypages":
                        option_cursor = pages
                    case "denypatterns":
                        option_cursor = patterns
                    case _:
                        option_cursor = None
            elif t == "BulletList":
                if option_cursor is not None:
                    for item in c:
                        assert isinstance(item, list)
                        assert len(item) == 1
                        it = item[0]["t"]
                        ic = item[0]["c"]
                        assert isinstance(it, str)
                        assert isinstance(ic, list)
                        if it == "Plain":
                            option_item_buffer = StringIO()
                            for ic_item in ic:
                                assert isinstance(ic_item, dict)
                                ic_t = ic_item["t"]
                                assert isinstance(ic_t, str)
                                if ic_t == "Str":
                                    ic_c = ic_item["c"]
                                    assert isinstance(ic_c, str)
                                    option_item_buffer.write(ic_c)
                                elif ic_t == "Space":
                                    option_item_buffer.write("_")
                            option_cursor.append(option_item_buffer.getvalue())
            else:
                option_cursor = None

        return cls(pages=pages, patterns=patterns)

    def filter_with_title(self, title: str) -> bool:
        if self.pages and title in self.pages:
            return False

        if self.patterns:
            for pattern in self.patterns:
                if match(pattern, title) is not None:
                    return False

        return True
