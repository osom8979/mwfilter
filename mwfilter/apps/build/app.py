# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, NamedTuple, Optional

import yaml
from type_serialize import deserialize

from mwfilter.arguments import METHOD_VERSIONS
from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath, exclude_filepath
from mwfilter.mw.convert_info import ConvertInfo
from mwfilter.mw.exclude import Exclude
from mwfilter.pandoc.markdown.dumper import PandocToMarkdownDumper
from mwfilter.paths.expand_abspath import expand_abspath
from mwfilter.system.ask import ask_continue, ask_overwrite


class BuildTuple(NamedTuple):
    i: int
    max_index: int
    docs_dirpath: Path
    method_version: int
    info: ConvertInfo
    dumper: PandocToMarkdownDumper


class ExcludeTuple(NamedTuple):
    exclude: Exclude
    info: ConvertInfo


class BuildApp:
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
        assert isinstance(args.method_version, int)
        assert args.method_version in METHOD_VERSIONS
        assert isinstance(args.mkdocs_yml, str)
        assert isinstance(args.all, bool)
        assert isinstance(args.dry_run, bool)
        assert isinstance(args.pages, list)
        assert isinstance(args.start_index, int)
        assert isinstance(args.jobs, int)

        self._hostname = args.hostname
        self._yes = args.yes
        self._ignore_errors = args.ignore_errors
        self._debug = args.debug
        self._verbose = args.verbose
        self._method_version = args.method_version
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._exclude_yml = exclude_filepath(args.cache_dir, self._hostname)
        self._start_index = args.start_index
        self._mkdocs_yml = Path(expand_abspath(args.mkdocs_yml))
        self._all = args.all
        self._dry_run = args.dry_run
        self._pages = list(str(page_name) for page_name in args.pages)
        self._jobs = args.jobs if 1 <= args.jobs else (cpu_count() * 2)

    @staticmethod
    def find_json_files_recursively(root_dir: Path) -> List[Path]:
        result = list()
        for dirpath, dirnames, filenames in root_dir.walk():
            for filename in filenames:
                if filename.endswith(".json"):
                    result.append(dirpath / filename)
        return result

    def all_json_files(self) -> List[Path]:
        return self.find_json_files_recursively(self._pages_dir)

    def specified_json_files(self) -> List[Path]:
        result = list()
        for page_name in self._pages:
            filepath = self._pages_dir / (page_name + ".json")
            if not filepath.is_file():
                raise FileNotFoundError(f"Not found JSON file: '{str(filepath)}'")
            result.append(filepath)
        return result

    def selected_json_files(self) -> List[Path]:
        if self._all:
            return self.all_json_files()
        else:
            return self.specified_json_files()

    def create_convert_infos(self) -> List[ConvertInfo]:
        json_filenames = self.selected_json_files()
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

    @staticmethod
    def build(item: BuildTuple) -> None:
        i = item.i
        max_index = item.max_index
        docs_dirpath = item.docs_dirpath
        method_version = item.method_version
        info = item.info
        dumper = item.dumper

        logger.info(f"Converting ({i}/{max_index}) {info.filename} ...")

        path = docs_dirpath / info.markdown_filename
        info_ver = info.meta.method_version
        ver = info_ver if info_ver is not None else method_version
        try:
            text = info.as_markdown(ver, dumper=dumper)
        except BaseException as e:
            logger.error(f"Convert error ({i}/{max_index}) {info.filename} ... {e}")
            raise
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    @staticmethod
    def exclude_filter(item: ExcludeTuple) -> Optional[ConvertInfo]:
        exclude = item.exclude
        info = item.info

        if not exclude.filter_with_title(info.filename):
            logger.warning(f"Filtered page: '{info.filename}'")
            return None

        return info

    def run(self) -> None:
        if not self._mkdocs_yml.is_file():
            mkdocs_yml = str(self._mkdocs_yml)
            raise FileNotFoundError(f"Not found mkdocs config file: '{mkdocs_yml}'")

        if not self._exclude_yml.is_file():
            exclude_yml = str(self._exclude_yml)
            raise FileNotFoundError(f"Not found exclude file: '{exclude_yml}'")

        with self._exclude_yml.open("rt", encoding="utf-8") as f:
            exclude = deserialize(yaml.safe_load(f), Exclude)
            assert isinstance(exclude, Exclude)

        exclude_args: List[ExcludeTuple] = list()
        for si in self.create_convert_infos():
            exclude_args.append(ExcludeTuple(exclude, si))

        infos = dict()

        if 1 <= self._jobs:
            with Pool(processes=self._jobs) as pool:
                result = pool.map(self.exclude_filter, exclude_args)
                assert isinstance(result, list)
                for ci in result:
                    if ci is None:
                        continue
                    assert isinstance(ci, ConvertInfo)
                    infos[ci.filename] = ci
        else:
            for exclude_arg in exclude_args:
                if ci := self.exclude_filter(exclude_arg):
                    assert isinstance(ci, ConvertInfo)
                    infos[ci.filename] = ci

        with self._mkdocs_yml.open("rt", encoding="utf-8") as f:
            mkdocs = yaml.safe_load(f)

        if not isinstance(mkdocs, dict):
            raise TypeError(f"Unexpected mkdocs types: {type(mkdocs).__name__}")

        site_name = mkdocs.get("site_name")
        logger.info(f"Site name: '{site_name}'")

        docs_dir = mkdocs.get("docs_dir", "docs")
        logger.info(f"Docs dir: '{docs_dir}'")

        docs_dirpath = self._mkdocs_yml.parent / docs_dir
        values = list(infos.values())
        source_count = len(infos)
        max_index = source_count - 1
        dumper = PandocToMarkdownDumper(list(infos.keys()), no_abspath=True)

        if self._yes and not self._dry_run:
            build_args: List[BuildTuple] = list()
            for i in range(self._start_index, source_count):
                item = BuildTuple(
                    i,
                    max_index,
                    docs_dirpath,
                    self._method_version,
                    values[i],
                    dumper,
                )
                build_args.append(item)

            with Pool(processes=self._jobs) as pool:
                pool.map(self.build, build_args)
        else:
            for i in range(self._start_index, source_count):
                info = values[i]
                logger.info(f"Convert ({i}/{max_index}): {info.filename}")
                markdown_path = docs_dirpath / info.markdown_filename

                if not ask_overwrite(markdown_path, force_yes=self._yes):
                    continue

                if info.meta.method_version is not None:
                    method_version = info.meta.method_version
                else:
                    method_version = self._method_version

                markdown_text = info.as_markdown(method_version, dumper=dumper)

                if not self._yes and self._debug and 2 <= self._verbose:
                    hr = "-" * 88
                    print(f"{hr}\nMediaWiki content:\n{info.text}\n{hr}")
                    print(f"{hr}\nMarkdown content:\n{markdown_text}\n{hr}")
                    if not ask_continue():
                        continue

                if self._dry_run:
                    continue

                markdown_path.parent.mkdir(parents=True, exist_ok=True)
                markdown_path.write_text(markdown_text)
