# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass
class Citation:
    # id_: str
    # prefix: List[Inline]
    # suffix: List[Inline]
    # mode: CitationMode
    # notenum: int
    # hash: int

    @classmethod
    def parse_object(cls, e):
        return cls()

    @classmethod
    def parse_object_with_list(cls, e):
        return list(cls.parse_object(item) for item in e)
