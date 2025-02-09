# -*- coding: utf-8 -*-

from typing import Protocol, TypeVar, runtime_checkable

_T = TypeVar("_T")


@runtime_checkable
class MetaValue[_T](Protocol):
    content: _T

    @classmethod
    def parse_object(cls, e): ...

    def serialize(self): ...
