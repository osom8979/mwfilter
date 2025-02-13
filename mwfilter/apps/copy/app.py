# -*- coding: utf-8 -*-

import json
import os
from argparse import Namespace

from type_serialize import deserialize, serialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath
from mwfilter.mw.page_meta import PageMeta
from mwfilter.system.ask import ask_overwrite


class CopyApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)

        # Subparser arguments
        assert isinstance(args.src, str)
        assert isinstance(args.dest, str)
        assert isinstance(args.namespace, (type(None), int))
        assert isinstance(args.method_version, (type(None), int))

        self._hostname = args.hostname
        self._yes = args.yes
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)

        self._src = args.src
        self._dest = args.dest
        self._namespace = args.namespace
        self._method_version = args.method_version

    def save(self, meta: PageMeta, content: str) -> None:
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
        if not self._src:
            raise ValueError("The 'src' argument is required")

        json_path = self._pages_dir / f"{self._src}.json"
        wiki_path = self._pages_dir / f"{self._src}.wiki"

        if not json_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")
        if not wiki_path.is_file():
            raise FileNotFoundError(f"File not found: '{str(wiki_path)}'")

        json_text = json_path.read_bytes()
        json_obj = json.loads(json_text)
        meta = deserialize(json_obj, PageMeta)
        assert isinstance(meta, PageMeta)
        content = wiki_path.read_text()

        meta.name = self._dest
        meta.page_title = self._dest
        meta.base_title = self._dest
        meta.base_name = self._dest
        if self._namespace is not None:
            meta.namespace = self._namespace
        if self._method_version is not None:
            meta.method_version = self._method_version

        self.save(meta, content)
        logger.info(f"Copy complete: '{self._src}' -> '{self._dest}'")
