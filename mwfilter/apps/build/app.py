# -*- coding: utf-8 -*-

import json
import os
from argparse import Namespace
from hashlib import sha256
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

import yaml
from type_serialize import deserialize

from mwfilter import __version__ as mwfilter_version
from mwfilter.arguments import METHOD_VERSIONS
from mwfilter.logging.logging import logger
from mwfilter.arguments import DEFAULT_IMAGE_PAGE
from mwfilter.mw.cache_dirs import (
    build_stamp_filepath,
    exclude_filepath,
    pages_cache_dirpath,
)
from mwfilter.mw.convert_info import ConvertInfo
from mwfilter.mw.exclude import Exclude
from mwfilter.mw.image_list import ImageList
from mwfilter.pandoc.markdown.dumper import PandocToMarkdownDumper
from mwfilter.paths.expand_abspath import expand_abspath
from mwfilter.system.ask import ask_continue, ask_overwrite


class BuildTuple(NamedTuple):
    i: int
    max_index: int
    docs_dirpath: Path
    method_version: int
    info: ConvertInfo
    filenames: List[str]
    image_names: List[str]


class ExcludeTuple(NamedTuple):
    exclude: Exclude
    info: ConvertInfo


class BuildError(Exception):
    pass


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
        assert isinstance(args.changed, bool)
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
        self._build_stamp_json = build_stamp_filepath(args.cache_dir, self._hostname)
        self._start_index = args.start_index
        self._mkdocs_yml = Path(expand_abspath(args.mkdocs_yml))
        self._all = args.all
        self._changed = args.changed
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
        filenames = item.filenames
        image_names = item.image_names
        dumper = PandocToMarkdownDumper(
            filenames,
            no_abspath=True,
            image_names=image_names,
        )

        logger.info(f"Converting ({i}/{max_index}) {info.filename} ...")

        path = docs_dirpath / info.markdown_filename
        info_ver = info.meta.method_version
        ver = info_ver if info_ver is not None else method_version
        try:
            text = info.as_markdown(ver, dumper=dumper)
        except BaseException as e:
            raise BuildError(f"Convert error ({i}/{max_index}) {info.filename}") from e
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

    def build_stamp(self, filenames: List[str], image_names: List[str]) -> str:
        # Inputs shared by every page; any change can alter the output of all pages
        stamp = {
            "mwfilter_version": mwfilter_version,
            "method_version": self._method_version,
            "exclude": sha256(self._exclude_yml.read_bytes()).hexdigest(),
            "filenames": sorted(filenames),
            "image_names": sorted(image_names),
        }
        return sha256(json.dumps(stamp).encode("utf-8")).hexdigest()

    def read_build_stamps(self) -> Dict[str, str]:
        if not self._build_stamp_json.is_file():
            return dict()
        try:
            stamps = json.loads(self._build_stamp_json.read_text())
        except BaseException as e:
            logger.warning(f"Unreadable build stamp file: {e}")
            return dict()
        return stamps if isinstance(stamps, dict) else dict()

    def write_build_stamp(self, docs_dirpath: Path, stamp: str) -> None:
        stamps = self.read_build_stamps()
        stamps[str(docs_dirpath)] = stamp
        self._build_stamp_json.write_text(json.dumps(stamps, indent=2))

    @staticmethod
    def is_outdated(docs_dirpath: Path, info: ConvertInfo) -> bool:
        markdown_path = docs_dirpath / info.markdown_filename
        if not markdown_path.is_file():
            return True
        markdown_mtime = markdown_path.stat().st_mtime
        meta_mtime = Path(info.meta_path).stat().st_mtime
        text_mtime = Path(info.text_path).stat().st_mtime
        return markdown_mtime < max(meta_mtime, text_mtime)

    def run(self) -> None:
        if self._changed and not self._all:
            raise ValueError("The '--changed' argument requires '--all'")

        if not self._mkdocs_yml.is_file():
            mkdocs_yml = str(self._mkdocs_yml)
            raise FileNotFoundError(f"Not found mkdocs config file: '{mkdocs_yml}'")

        if not self._exclude_yml.is_file():
            exclude_yml = str(self._exclude_yml)
            raise FileNotFoundError(f"Not found exclude file: '{exclude_yml}'")

        with self._exclude_yml.open("rt", encoding="utf-8") as f:
            exclude = deserialize(yaml.safe_load(f), Exclude)
            assert isinstance(exclude, Exclude)

        image_names: List[str] = list()
        image_wiki_path = self._pages_dir / f"{DEFAULT_IMAGE_PAGE}.wiki"
        if image_wiki_path.is_file():
            mediawiki_content = image_wiki_path.read_text()
            image_list = ImageList.from_mediawiki_content(mediawiki_content)
            image_names = image_list.images
            logger.info(f"Loaded {len(image_names)} image names from whitelist")

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
        filenames = list(infos.keys())

        build_stamp = str()
        if self._changed:
            build_stamp = self.build_stamp(filenames, image_names)
            prev_stamp = self.read_build_stamps().get(str(docs_dirpath))
            if build_stamp == prev_stamp:
                values = [v for v in values if self.is_outdated(docs_dirpath, v)]
                logger.info(f"Changed pages: {len(values)}/{len(infos)}")
            else:
                logger.info("Build inputs have changed; build all pages")

        source_count = len(values)
        max_index = source_count - 1

        if self._yes and not self._dry_run:
            build_args: List[BuildTuple] = list()
            for i in range(self._start_index, source_count):
                item = BuildTuple(
                    i,
                    max_index,
                    docs_dirpath,
                    self._method_version,
                    values[i],
                    filenames,
                    image_names,
                )
                build_args.append(item)

            with Pool(processes=self._jobs) as pool:
                pool.map(self.build, build_args)

            if build_stamp:
                self.write_build_stamp(docs_dirpath, build_stamp)
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

                dumper = PandocToMarkdownDumper(
                    filenames,
                    no_abspath=True,
                    image_names=image_names,
                )
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
