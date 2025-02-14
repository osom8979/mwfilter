# -*- coding: utf-8 -*-

from re import IGNORECASE, Pattern
from re import compile as re_compile

REDIRECT_REGEX: Pattern[str] = re_compile(r"^#REDIRECT\s*\[\[(.*)]]", flags=IGNORECASE)
"""
https://www.mediawiki.org/wiki/Help:Redirects#Creating_a_redirect
"""


def parse_redirect_pagename(text: str) -> str:
    if match := REDIRECT_REGEX.match(text.strip()):
        return match.group(1)
    raise ValueError(f"Invalid redirect page name: {text}")
