# -*- coding: utf-8 -*-

from re import Pattern
from re import compile as re_compile

PREFIX_SLASHES: Pattern[str] = re_compile(r"^/+")


def remove_prefix_slashes(s: str) -> str:
    return PREFIX_SLASHES.sub(str(), s)
