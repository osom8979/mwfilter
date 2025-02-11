# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

_T = TypeVar("_T")


class MetaValue(ABC, Generic[_T]):
    content: _T

    @classmethod
    @abstractmethod
    def parse_object(cls, e):
        raise NotImplementedError

    @abstractmethod
    def serialize(self):
        raise NotImplementedError
