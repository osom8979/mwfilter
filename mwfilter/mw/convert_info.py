# -*- coding: utf-8 -*-

import json
import urllib.parse
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Sequence

from pypandoc import convert_file
from type_serialize import deserialize

from mwfilter.assets import get_markdown_filter_lua
from mwfilter.mw.page_meta import PageMeta


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
    def yaml_frontmatter(self):
        buffer = StringIO()
        buffer.write("---\n")
        buffer.write(f"title: {self.name}\n")
        buffer.write(f"date: {self.date}\n")
        buffer.write("---\n")
        buffer.write("\n")
        return buffer.getvalue()

    def as_markdown(self) -> str:
        return self.yaml_frontmatter + convert_file(
            self.text_path,
            to="markdown",
            format="mediawiki",
            filters=[get_markdown_filter_lua()],
        )


def find_convert_info(infos: Sequence[ConvertInfo], page_name: str) -> ConvertInfo:
    for info in infos:
        if info.name == page_name:
            return info
    raise IndexError("Not found settings page")
