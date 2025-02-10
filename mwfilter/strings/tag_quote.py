# -*- coding: utf-8 -*-

from contextlib import contextmanager
from io import StringIO
from typing import Literal, Optional


@contextmanager
def tag_quote(
    buffer: StringIO,
    tag: str,
    *,
    markdown: Optional[Literal[1, "block", "span"]] = 1,
    newline: Optional[str] = "\n",
    **kwargs,
):
    buffer.write(f"<{tag}")
    if markdown is not None:
        # https://python-markdown.github.io/extensions/md_in_html/
        buffer.write(f' markdown="{markdown}"')
    if kwargs:
        for k, v in kwargs.items():
            buffer.write(f' {k}="{v}"')
    buffer.write(">")
    if newline:
        buffer.write(newline)
    try:
        yield buffer
    finally:
        if newline:
            buffer.write(newline)
        buffer.write(f"</{tag}>")
        if newline:
            buffer.write(newline)
