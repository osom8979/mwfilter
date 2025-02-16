# -*- coding: utf-8 -*-

import json
import urllib.parse
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional

from pypandoc import convert_file
from type_serialize import deserialize

from mwfilter.arguments import DEFAULT_METHOD_VERSION
from mwfilter.assets import get_markdown_filter_lua
from mwfilter.mw.page_meta import PageMeta
from mwfilter.mw.redirect import parse_redirect_pagename
from mwfilter.pandoc.ast.pandoc import Pandoc
from mwfilter.pandoc.markdown.dumper import PandocToMarkdownDumper


@dataclass
class ConvertInfo:
    meta_path: str = field(default_factory=str)
    text_path: str = field(default_factory=str)
    meta: PageMeta = field(default_factory=lambda: PageMeta())
    text: str = field(default_factory=str)

    @classmethod
    def from_paths(cls, meta_path: Path, text_path: Path):
        return cls(
            meta_path=str(meta_path),
            text_path=str(text_path),
            meta=deserialize(json.loads(meta_path.read_bytes()), PageMeta),
            text=text_path.read_text(),
        )

    @property
    def name(self):
        return self.meta.name

    @property
    def filename(self):
        return self.meta.filename

    @property
    def json_filename(self) -> str:
        return self.meta.json_filename

    @property
    def wiki_filename(self) -> str:
        return self.meta.wiki_filename

    @property
    def markdown_filename(self) -> str:
        return self.meta.markdown_filename

    @property
    def date(self):
        return self.meta.touched.date().isoformat()

    @property
    def url_name(self):
        return urllib.parse.quote(self.name)

    @property
    def redirect_pagename(self) -> str:
        try:
            return PageMeta.normalize_page_name(parse_redirect_pagename(self.text))
        except ValueError:
            return str()

    @property
    def yaml_frontmatter(self):
        buffer = StringIO()
        buffer.write("---\n")
        buffer.write(f"title: {self.name}\n")
        buffer.write(f"date: {self.date}\n")
        buffer.write("---\n")
        buffer.write("\n")
        return buffer.getvalue()

    def as_markdown(
        self,
        version=DEFAULT_METHOD_VERSION,
        *,
        dumper: Optional[PandocToMarkdownDumper] = None,
    ) -> str:
        match version:
            case 1:
                return self.as_markdown_v1()
            case 2:
                return self.as_markdown_v2(dumper)
            case _:
                raise ValueError(f"Unsupported method version: {version}")

    def as_markdown_v1(self) -> str:
        return self.yaml_frontmatter + convert_file(
            self.text_path,
            to="markdown",
            format="mediawiki",
            filters=[get_markdown_filter_lua()],
        )

    def as_markdown_v2(self, dumper: Optional[PandocToMarkdownDumper] = None) -> str:
        if dumper is None:
            dumper = PandocToMarkdownDumper(no_abspath=True)
        assert dumper is not None
        with open(self.text_path, "rt") as f:
            pandoc = Pandoc.parse_text(f.read())
            return dumper.dump(pandoc, self.meta)
