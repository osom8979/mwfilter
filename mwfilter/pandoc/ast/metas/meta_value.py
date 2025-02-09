# -*- coding: utf-8 -*-

from typing import Protocol, TypeVar

_T = TypeVar("_T")


class MetaValue[_T](Protocol):
    content: _T

    @classmethod
    def parse_object(cls, e):
        pass
