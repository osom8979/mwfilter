# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from glob import glob
from typing import List
from pathlib import Path

import yaml

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath
from mwfilter.mw.convert_info import ConvertInfo
from mwfilter.mw.settings import Settings
from mwfilter.paths.expand_abspath import expand_abspath
from mwfilter.system.ask import ask_overwrite


class BuildApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)
        assert isinstance(args.ignore_errors, bool)

        # Subparser arguments
        assert isinstance(args.mkdocs_yml, str)

        self._hostname = args.hostname
        self._yes = args.yes
        self._ignore_errors = args.ignore_errors
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._settings_page = args.settings_page
        self._mkdocs_yml = Path(expand_abspath(args.mkdocs_yml))

    def create_convert_infos(self) -> List[ConvertInfo]:
        json_filenames = glob("*.json", root_dir=self._pages_dir, recursive=True)
        if not json_filenames:
            raise FileNotFoundError(f"No JSON files found in '{self._pages_dir}'")

        json_filenames.sort()
        count = len(json_filenames)
        result = list()

        for i, json_filename in enumerate(json_filenames, start=1):
            filename = os.path.splitext(json_filename)[0]
            logger.debug(f"Read ({i}/{count}): {filename}")

            try:
                json_path = self._pages_dir / json_filename
                wiki_path = self._pages_dir / f"{filename}.wiki"
                info = ConvertInfo.from_paths(json_path, wiki_path)
                result.append(info)
            except BaseException as e:
                if self._ignore_errors:
                    logger.error(e)
                else:
                    raise
        return result

    def run(self) -> None:
        if not self._mkdocs_yml.is_file():
            mkdocs_yml = str(self._mkdocs_yml)
            raise FileNotFoundError(f"Not found mkdocs config file: '{mkdocs_yml}'")

        infos = self.create_convert_infos()
        settings = Settings()

        filtered_infos = list()
        for info in infos:
            if not settings.filter_with_title(info.filename):
                logger.warning(f"Filtered page: '{info.filename}'")
                continue
            filtered_infos.append(info)

        with self._mkdocs_yml.open("rt", encoding="utf-8") as f:
            mkdocs = yaml.safe_load(f)

        if not isinstance(mkdocs, dict):
            raise TypeError(f"Unexpected mkdocs types: {type(mkdocs).__name__}")

        site_name = mkdocs.get("site_name")
        logger.info(f"Site name: '{site_name}'")

        docs_dir = mkdocs.get("docs_dir", "docs")
        logger.info(f"Docs dir: '{docs_dir}'")

        docs_dirpath = self._mkdocs_yml.parent / docs_dir
        count = len(infos)
        for i, info in enumerate(infos, start=1):
            logger.info(f"Convert ({i}/{count}): {info.filename}")
            markdown_path = docs_dirpath / info.markdown_filename
            if ask_overwrite(markdown_path, force_yes=self._yes):
                markdown_path.parent.mkdir(parents=True, exist_ok=True)
                markdown_path.write_text(info.as_markdown())
