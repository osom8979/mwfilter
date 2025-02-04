# -*- coding: utf-8 -*-

import os
from argparse import Namespace
from typing import List

from mwfilter.mw.cache_dirs import pickle_cache_filepath
from mwfilter.mw.convert_info import ConvertInfo, load_convert_infos


class ConvertApp:
    _infos: List[ConvertInfo]

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
        self._pickle_path = pickle_cache_filepath(args.cache_dir, self._hostname)

    def run(self) -> None:
        if not self._pickle_path.is_file():
            path = str(self._pickle_path)
            raise FileNotFoundError(f"Pickled file not found: '{path}'")

        infos = load_convert_infos(self._pickle_path)
        # settings = find_settings(infos, settings_page)
        # infos = list(filter(lambda i: settings.filter(i), infos))
        #
        # logger.info("Write all output pages ...")
        # with tqdm(total=len(infos)) as progress_bar:
        #     for info in infos:
        #         try:
        #             output_path = Path(docs) / f"{info.filename}.md"
        #             if output_path.is_file():
        #                 continue
        #             output_path.parent.mkdir(parents=True, exist_ok=True)
        #             output_path.write_text(info.as_markdown())
        #         finally:
        #             progress_bar.update()
        #
        # if mkdocs_yml:
        #     mkdocs_yml_path = Path(mkdocs_yml)
        #     if mkdocs_yml_path.is_file():
        #         with mkdocs_yml_path.open("rt", encoding="utf-8") as f:
        #             mkdocs_obj = yaml.safe_load(f)
        #     else:
        #         mkdocs_obj = dict()
        #
        #     assert isinstance(mkdocs_obj, dict)
        #     site_name = mkdocs_obj.get("site_name")
        #     if site_name:
        #         logger.info(f"Site name: '{site_name}'")
        pass
