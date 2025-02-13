# -*- coding: utf-8 -*-

import json
import os
from argparse import Namespace

from type_serialize import serialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath
from mwfilter.mw.convert_info import ConvertInfo
from mwfilter.mw.namespace import MAIN_NAMESPACE
from mwfilter.system.ask import ask_overwrite


class NavApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)

        # Subparser arguments
        assert isinstance(args.navigation_page, str)
        assert isinstance(args.to, str)

        self._hostname = args.hostname
        self._yes = args.yes
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._navigation_page = args.navigation_page
        self._to = args.to

    def convert_to(self, info: ConvertInfo) -> None:
        meta = info.meta
        content = info.text
        meta_json = json.dumps(serialize(meta))

        json_path = self._pages_dir / meta.json_filename
        wiki_path = self._pages_dir / meta.wiki_filename

        try:
            if ask_overwrite(json_path, force_yes=self._yes):
                json_path.parent.mkdir(parents=True, exist_ok=True)
                json_path.write_text(meta_json)
            if ask_overwrite(wiki_path, force_yes=self._yes):
                wiki_path.parent.mkdir(parents=True, exist_ok=True)
                wiki_path.write_text(content)
        except BaseException as e:
            json_path.unlink(missing_ok=True)
            wiki_path.unlink(missing_ok=True)
            logger.error(e)
            raise

    def run(self) -> None:
        if not self._navigation_page:
            raise ValueError("The 'navigation_page' argument is required")

        json_path = self._pages_dir / f"{self._navigation_page}.json"
        wiki_path = self._pages_dir / f"{self._navigation_page}.wiki"

        if not json_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")
        if not wiki_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")

        info = ConvertInfo.from_paths(json_path, wiki_path)
        info.meta.name = self._to
        info.meta.page_title = self._to
        info.meta.base_title = self._to
        info.meta.base_name = self._to
        info.meta.namespace = MAIN_NAMESPACE
        info.meta.redirect = False

        self.convert_to(info)
