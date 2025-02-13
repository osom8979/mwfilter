# -*- coding: utf-8 -*-

import os
from argparse import Namespace

import yaml
from type_serialize import serialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import exclude_filepath, pages_cache_dirpath
from mwfilter.mw.exclude import Exclude
from mwfilter.system.ask import ask_overwrite


class ExcludeApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)

        # Subparser arguments
        assert isinstance(args.exclude_page, str)
        assert isinstance(args.stdout, bool)

        self._hostname = args.hostname
        self._yes = args.yes
        self._exclude_page = args.exclude_page
        self._stdout = args.stdout
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._exclude_path = exclude_filepath(args.cache_dir, self._hostname)

    def run(self) -> None:
        if not self._exclude_page:
            raise ValueError("The 'exclude_page' argument is required")

        wiki_path = self._pages_dir / f"{self._exclude_page}.wiki"
        if not wiki_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")

        logger.debug(f"Read exclude wiki file: '{wiki_path}'")
        mediawiki_content = wiki_path.read_text()
        exclude = Exclude.from_mediawiki_content(mediawiki_content)
        exclude_text = serialize(exclude)

        if self._stdout:
            print(exclude_text)
            return

        if ask_overwrite(self._exclude_path, force_yes=self._yes):
            self._exclude_path.parent.mkdir(parents=True, exist_ok=True)
            with self._exclude_path.open("wt") as f:
                yaml.dump(exclude_text, f)
