# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from pathlib import Path
from shutil import rmtree

from mwfilter.logging.logging import logger


class ClearApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        assert isinstance(args.all, bool)
        assert isinstance(args.ignore_errors, bool)

        self._hostname = args.hostname
        self._cache_dir = args.cache_dir
        self._all = args.all
        self._ignore_errors = args.ignore_errors

    def run(self) -> None:
        remove_dir = Path(self._cache_dir)
        if not self._all:
            remove_dir = remove_dir / self._hostname

        if remove_dir.is_dir():
            logger.info(f"Clear cache directory: '{str(remove_dir)}'")
            rmtree(remove_dir, ignore_errors=self._ignore_errors)
        else:
            logger.warning(f"Not a cache directory: '{str(remove_dir)}'")
