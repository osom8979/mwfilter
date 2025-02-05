# -*- coding: utf-8 -*-

import json
from dataclasses import dataclass, field
from io import StringIO
from re import match
from typing import List, Optional

from pypandoc import convert_text


@dataclass
class Settings:
    allow_pages: List[str] = field(default_factory=list)
    allow_patterns: List[str] = field(default_factory=list)
    deny_pages: List[str] = field(default_factory=list)
    deny_patterns: List[str] = field(default_factory=list)

    @classmethod
    def from_mediawiki_content(cls, mediawiki_content: str):
        info_json = convert_text(mediawiki_content, to="json", format="mediawiki")
        info_obj = json.loads(info_json)
        assert isinstance(info_obj, dict)
        blocks = info_obj["blocks"]
        assert isinstance(blocks, list)

        allow_pages: List[str] = list()
        allow_patterns: List[str] = list()
        deny_pages: List[str] = list()
        deny_patterns: List[str] = list()

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
                    case "allowpages":
                        option_cursor = allow_pages
                    case "allowpatterns":
                        option_cursor = allow_patterns
                    case "denypages":
                        option_cursor = deny_pages
                    case "denypatterns":
                        option_cursor = deny_patterns
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

        return cls(
            allow_pages=allow_pages,
            allow_patterns=allow_patterns,
            deny_pages=deny_pages,
            deny_patterns=deny_patterns,
        )

    def filter_with_title(self, title: str) -> bool:
        if self.allow_pages and title in self.allow_pages:
            return True

        if self.allow_patterns:
            for pattern in self.deny_patterns:
                if match(pattern, title) is not None:
                    return True

        if self.deny_pages and title in self.deny_pages:
            return False

        if self.deny_patterns:
            for pattern in self.deny_patterns:
                if match(pattern, title) is not None:
                    return False

        return True
