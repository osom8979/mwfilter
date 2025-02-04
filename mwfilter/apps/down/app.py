# -*- coding: utf-8 -*-

import json
import os
from argparse import Namespace
from typing import Optional, Sequence, Tuple

from mwclient import Site
from mwclient.page import Page
from type_serialize import serialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import pages_cache_dirpath
from mwfilter.mw.page_meta import PageMeta


class DownApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.username, (type(None), str))
        assert isinstance(args.password, (type(None), str))
        assert isinstance(args.endpoint_path, str)
        assert isinstance(args.namespace, int)
        assert isinstance(args.all, bool)
        assert isinstance(args.overwrite, bool)
        assert isinstance(args.pages, list)
        assert isinstance(args.cache_dir, str)
        assert isinstance(args.skip_errors, bool)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        if not args.endpoint_path:
            raise ValueError("The 'endpoint_path' argument is required")
        if args.namespace not in Site.default_namespaces:
            raise ValueError(f"Unexpected namespace number: {args.namespace}")
        if not args.all and not args.pages:
            raise ValueError("No page was specified to download")

        self._hostname = args.hostname
        self._username = args.username
        self._password = args.password
        self._endpoint_path = args.endpoint_path
        self._namespace = args.namespace
        self._all = args.all
        self._overwrite = args.overwrite
        self._pages = list(str(page_name) for page_name in args.pages)
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._skip_errors = args.skip_errors

    @property
    def auth(self) -> Optional[Tuple[str, str]]:
        if self._username and self._password:
            return self._username, self._password
        else:
            return None

    def create_site(self) -> Site:
        # return Site(host=self._hostname, path=self._endpoint_path, httpauth=self.auth)
        site = Site(host=self._hostname, path=self._endpoint_path)
        if auth := self.auth:
            site.login(*auth)
        return site

    def download_page(self, page: Page, i: Optional[int] = None) -> None:
        meta = PageMeta.from_page(page)
        meta_json = json.dumps(serialize(meta))
        page_content = page.text()

        prefix = f"Download page ({i})" if i is not None else "Download page"
        logger.info(f"{prefix}: {meta.filename}")

        json_path = self._pages_dir / f"{meta.filename}.json"
        wiki_path = self._pages_dir / f"{meta.filename}.wiki"

        try:
            if self._overwrite or not json_path.is_file():
                json_path.parent.mkdir(parents=True, exist_ok=True)
                json_path.unlink(missing_ok=True)
                json_path.write_text(meta_json)

            if self._overwrite or not wiki_path.is_file():
                wiki_path.parent.mkdir(parents=True, exist_ok=True)
                wiki_path.unlink(missing_ok=True)
                wiki_path.write_text(page_content)
        except BaseException as e:
            json_path.unlink(missing_ok=True)
            wiki_path.unlink(missing_ok=True)
            if self._skip_errors:
                logger.error(e)
            else:
                raise

    def download_allpages(self) -> None:
        site = self.create_site()
        for i, page in enumerate(site.allpages(namespace=self._namespace), start=1):
            self.download_page(page, i)

    def download_pages(self, page_names: Sequence[str]) -> None:
        site = self.create_site()
        for i, page_name in enumerate(page_names, start=1):
            try:
                page = site.pages[page_name]
            except BaseException as e:
                if self._skip_errors:
                    logger.error(e)
                else:
                    raise
            else:
                if isinstance(page, Page):
                    self.download_page(page, i)
                else:
                    error_message = f"Unexpected page type: {type(page).__name__}"
                    if self._skip_errors:
                        logger.error(error_message)
                    else:
                        raise TypeError(error_message)

    def run(self) -> None:
        if self._all:
            self.download_allpages()
        else:
            self.download_pages(self._pages)
