# -*- coding: utf-8 -*-

from pathlib import Path

from mwfilter.arguments import DEFAULT_EXCLUDE_YML, DEFAULT_PAGES_DIRNAME


def pages_cache_dirpath(
    cache_dir: str,
    hostname: str,
    pages_dirname=DEFAULT_PAGES_DIRNAME,
) -> Path:
    return Path(cache_dir) / hostname / pages_dirname


def exclude_filepath(
    cache_dir: str,
    hostname: str,
    exclude_filename=DEFAULT_EXCLUDE_YML,
) -> Path:
    return Path(cache_dir) / hostname / exclude_filename
