# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class Block(ABC):
    @classmethod
    @abstractmethod
    def parse_object(cls, e):
        raise NotImplementedError
