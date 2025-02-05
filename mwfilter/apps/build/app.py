# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from typing import List
from pathlib import Path

import yaml
from type_serialize import deserialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath, settings_filepath
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
        self._settings_yml = settings_filepath(args.cache_dir, self._hostname)
        self._mkdocs_yml = Path(expand_abspath(args.mkdocs_yml))

    @staticmethod
    def find_json_files_recursively(root_dir: Path) -> List[Path]:
        result = list()
        for dirpath, dirnames, filenames in root_dir.walk():
            for filename in filenames:
                if filename.endswith(".json"):
                    result.append(dirpath / filename)
        return result

    def create_convert_infos(self) -> List[ConvertInfo]:
        json_filenames = self.find_json_files_recursively(self._pages_dir)
        if not json_filenames:
            raise FileNotFoundError(f"No JSON files found in '{self._pages_dir}'")

        json_filenames.sort()
        count = len(json_filenames)
        result = list()

        for i, json_path in enumerate(json_filenames, start=1):
            filename = json_path.name.removesuffix(".json")
            logger.debug(f"Read ({i}/{count}): {filename}")

            try:
                wiki_path = json_path.parent / f"{filename}.wiki"
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

        if not self._settings_yml.is_file():
            settings_yml = str(self._settings_yml)
            raise FileNotFoundError(f"Not found settings file: '{settings_yml}'")

        with self._settings_yml.open("rt", encoding="utf-8") as f:
            settings = deserialize(yaml.safe_load(f), Settings)
            assert isinstance(settings, Settings)

        infos = self.create_convert_infos()

        redirected_infos = list()
        source_infos = dict()

        for info in infos:
            if not settings.filter_with_title(info.filename):
                logger.warning(f"Filtered page: '{info.filename}'")
                continue
            if info.meta.redirect:
                redirected_infos.append(info)
            else:
                source_infos[info.filename] = info

        for info in redirected_infos:
            redirect_pagename = info.redirect_pagename
            if source_info := source_infos.get(redirect_pagename):
                source_info.meta.append_alias(info.filename)

        with self._mkdocs_yml.open("rt", encoding="utf-8") as f:
            mkdocs = yaml.safe_load(f)

        if not isinstance(mkdocs, dict):
            raise TypeError(f"Unexpected mkdocs types: {type(mkdocs).__name__}")

        site_name = mkdocs.get("site_name")
        logger.info(f"Site name: '{site_name}'")

        docs_dir = mkdocs.get("docs_dir", "docs")
        logger.info(f"Docs dir: '{docs_dir}'")

        docs_dirpath = self._mkdocs_yml.parent / docs_dir
        source_count = len(source_infos)
        for i, info in enumerate(source_infos.values(), start=1):
            logger.info(f"Convert ({i}/{source_count}): {info.filename}")
            markdown_path = docs_dirpath / info.markdown_filename
            if ask_overwrite(markdown_path, force_yes=self._yes):
                markdown_path.parent.mkdir(parents=True, exist_ok=True)
                markdown_path.write_text(info.as_markdown())
