# -*- coding: utf-8 -*-

from functools import lru_cache
from types import MappingProxyType
from typing import Final

NamespaceMap = MappingProxyType[int, str]

MAIN_NAMESPACE: Final[int] = 0
PROJECT_NAMESPACE: Final[int] = 4
FILE_NAMESPACE: Final[int] = 6
TEMPLATE_NAMESPACE: Final[int] = 10


@lru_cache
def create_default_namespaces() -> NamespaceMap:
    return NamespaceMap(
        {
            -2: "Media",
            -1: "Special",
            0: "",  # Main
            1: "Talk",
            2: "User",
            3: "User talk",
            4: "Project",
            5: "Project talk",
            6: "File",
            7: "File talk",
            8: "MediaWiki",
            9: "MediaWiki talk",
            10: "Template",
            11: "Template talk",
            12: "Help",
            13: "Help talk",
            14: "Category",
            15: "Category talk",
        }
    )
