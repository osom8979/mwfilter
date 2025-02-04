# -*- coding: utf-8 -*-

from os.path import abspath, expanduser, expandvars


def expand_abspath(path: str) -> str:
    return abspath(expanduser(expandvars(path)))
