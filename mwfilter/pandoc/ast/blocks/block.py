# -*- coding: utf-8 -*-

from typing import Protocol


class Block(Protocol):
    @classmethod
    def parse_object(cls, e):
        pass
