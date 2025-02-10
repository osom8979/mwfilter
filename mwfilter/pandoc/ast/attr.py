# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Attr:
    """Attributes: identifier, classes, key-value pairs"""

    identifier: str = field(default_factory=str)
    classes: List[str] = field(default_factory=list)
    pairs: List[Tuple[str, str]] = field(default_factory=list)

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)

        identifier = e[0]
        assert isinstance(identifier, str)

        classes = list()
        for e_class in e[1]:
            assert isinstance(e_class, str)
            classes.append(e_class)

        pairs = list()
        for e_pair in e[2]:
            key = e_pair[0]
            value = e_pair[1]
            assert isinstance(key, str)
            assert isinstance(value, str)
            pairs.append((key, value))

        return cls(identifier, classes, pairs)

    @property
    def is_empty(self):
        return not self.identifier and not self.classes and not self.pairs

    @property
    def kwargs(self):
        return dict(self.pairs)
