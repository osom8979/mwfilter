# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Final

PAGES_DIRNAME: Final[str] = "pages"
SETTINGS_FILENAME: Final[str] = "settings.yml"


def pages_cache_dirpath(cache_dir: str, hostname: str) -> Path:
    return Path(cache_dir) / hostname / PAGES_DIRNAME


def settings_filepath(cache_dir: str, hostname: str) -> Path:
    return Path(cache_dir) / hostname / SETTINGS_FILENAME
