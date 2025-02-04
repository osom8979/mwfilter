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
from mwfilter.mw.find_settings import find_settings
from mwfilter.mw.settings import Settings
from mwfilter.paths.expand_abspath import expand_abspath


class BuildApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.settings_page, str)
        assert isinstance(args.mkdocs_yml, str)
        assert isinstance(args.hostname, str)
        assert isinstance(args.overwrite, bool)
        assert isinstance(args.cache_dir, str)
        assert isinstance(args.skip_errors, bool)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        self._hostname = args.hostname
        self._overwrite = args.overwrite
        self._skip_errors = args.skip_errors
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._settings_page = args.settings_page
        self._mkdocs_yml = Path(expand_abspath(args.mkdocs_yml))

        if not self._mkdocs_yml.is_file():
            mkdocs_yml = str(self._mkdocs_yml)
            raise FileNotFoundError(f"Not found mkdocs config file: '{mkdocs_yml}'")

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
                if self._skip_errors:
                    logger.error(e)
                else:
                    raise
        return result

    def convert_info(
        self,
        info: ConvertInfo,
        docs_dirpath: Path,
        i: int,
        count: int,
    ) -> None:
        logger.info(f"Convert ({i}/{count}): {info.filename}")

        markdown_path = docs_dirpath / f"{info.filename}.md"
        if markdown_path.is_file() and not self._overwrite:
            return

        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.unlink(missing_ok=True)
        markdown_path.write_text(info.as_markdown())

    def run(self) -> None:
        infos = self.create_convert_infos()
        settings = find_settings(infos, self._settings_page)
        if settings is None:
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
            self.convert_info(info, docs_dirpath, i, count)
