# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Final

PAGES_DIRNAME: Final[str] = "pages"


def pages_cache_dirpath(cache_dir: str, hostname: str) -> Path:
    return Path(cache_dir) / hostname / PAGES_DIRNAME
