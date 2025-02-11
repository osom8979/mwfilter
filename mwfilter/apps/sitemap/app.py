# -*- coding: utf-8 -*-

import os
from argparse import Namespace

import yaml
from type_serialize import deserialize

from mwfilter.mw.cache_dirs import pages_cache_dirpath, settings_filepath
from mwfilter.mw.settings import Settings


class SitemapApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)
        assert isinstance(args.ignore_errors, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)

        # Subparser arguments
        assert isinstance(args.sitemap_pagename, str)

        self._hostname = args.hostname
        self._yes = args.yes
        self._ignore_errors = args.ignore_errors
        self._debug = args.debug
        self._verbose = args.verbose
        self._sitemap_pagename = args.sitemap_pagename
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._settings_yml = settings_filepath(args.cache_dir, self._hostname)

    def run(self) -> None:
        if not self._settings_yml.is_file():
            settings_yml = str(self._settings_yml)
            raise FileNotFoundError(f"Not found settings file: '{settings_yml}'")

        with self._settings_yml.open("rt", encoding="utf-8") as f:
            settings = deserialize(yaml.safe_load(f), Settings)
            assert isinstance(settings, Settings)
