# -*- coding: utf-8 -*-

from typing import Protocol, runtime_checkable


@runtime_checkable
class Inline(Protocol):
    @classmethod
    def parse_object(cls, e):
        pass
