# -*- coding: utf-8 -*-

import os
from shutil import rmtree
from argparse import Namespace
from pathlib import Path

from mwfilter.logging.logging import logger


class ClearApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert isinstance(args.all, bool)
        assert isinstance(args.skip_errors, bool)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        self._hostname = args.hostname
        self._cache_dir = args.cache_dir
        self._all = args.all
        self._skip_errors = args.skip_errors

    def run(self) -> None:
        remove_dir = Path(self._cache_dir)
        if not self._all:
            remove_dir = remove_dir / self._hostname

        logger.info(f"Clear cache directory: '{str(remove_dir)}'")
        rmtree(remove_dir, ignore_errors=self._skip_errors)
