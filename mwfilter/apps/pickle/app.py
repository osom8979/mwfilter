# -*- coding: utf-8 -*-

import os
import pickle
from argparse import Namespace
from glob import glob
from typing import List

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath, pickle_cache_filepath
from mwfilter.mw.convert_info import ConvertInfo


class PickleApp:
    def __init__(self, args: Namespace):
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
        self._pickle_path = pickle_cache_filepath(args.cache_dir, self._hostname)

    def create_convert_infos(self) -> List[ConvertInfo]:
        json_filenames = glob("*.json", root_dir=self._pages_dir, recursive=True)
        json_filenames.sort()
        count = len(json_filenames)

        result = list()
        for i, json_filename in enumerate(json_filenames, start=1):
            filename = os.path.splitext(json_filename)[0]
            prefix = f"Convert info ({i}/{count})" if i is not None else "Convert info"
            logger.info(f"{prefix}: {filename}")

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

    def run(self) -> None:
        if self._pickle_path.is_file():
            if not self._overwrite:
                path = str(self._pickle_path)
                raise FileExistsError(f"Pickled file exists: '{path}'")

        infos = self.create_convert_infos()
        self._pickle_path.unlink(missing_ok=True)
        self._pickle_path.write_bytes(pickle.dumps(infos))
