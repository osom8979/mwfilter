# -*- coding: utf-8 -*-

import json
import os
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence, Set, Tuple

from mwclient import Site
from mwclient.listing import RevisionsIterator
from mwclient.page import Page
from type_serialize import serialize

from mwfilter.logging.logging import logger
from mwfilter.mw.cache_dirs import exclude_filepath, pages_cache_dirpath
from mwfilter.mw.page_meta import PageMeta
from mwfilter.mw.redirect import parse_redirect_pagename
from mwfilter.system.ask import ask_overwrite


class DownApp:
    def __init__(self, args: Namespace):
        assert isinstance(args.hostname, str)
        assert isinstance(args.cache_dir, str)
        assert args.hostname
        assert os.path.isdir(args.cache_dir)

        # Common arguments
        assert isinstance(args.yes, bool)
        assert isinstance(args.ignore_errors, bool)

        # Subparser arguments
        assert isinstance(args.endpoint_path, str)
        assert isinstance(args.username, (type(None), str))
        assert isinstance(args.password, (type(None), str))
        assert isinstance(args.namespace, int)
        assert isinstance(args.no_expand_templates, bool)
        assert isinstance(args.all, bool)
        assert isinstance(args.changed, bool)
        assert isinstance(args.prune, bool)
        assert isinstance(args.pages, list)

        self._hostname = args.hostname
        self._yes = args.yes
        self._ignore_errors = args.ignore_errors
        self._endpoint_path = args.endpoint_path
        self._username = args.username
        self._password = args.password
        self._namespace = args.namespace
        self._no_expand_templates = args.no_expand_templates
        self._all = args.all
        self._changed = args.changed
        self._prune = args.prune
        self._pages_dir = pages_cache_dirpath(args.cache_dir, self._hostname)
        self._exclude_path = exclude_filepath(args.cache_dir, self._hostname)
        self._pages = list(str(page_name) for page_name in args.pages)

    @property
    def auth(self) -> Optional[Tuple[str, str]]:
        if self._username and self._password:
            return self._username, self._password
        else:
            return None

    def create_site(self) -> Site:
        site = Site(host=self._hostname, path=self._endpoint_path)
        if auth := self.auth:
            site.login(*auth)
        return site

    def page_to_meta(self, page: Page) -> Tuple[PageMeta, str]:
        revisions = page.revisions()
        assert isinstance(revisions, RevisionsIterator)
        meta = PageMeta.from_page(page)
        revs = list(revisions)
        meta.authors = list(set(rev["user"] for rev in revs))
        meta.edits = len(revs)
        if revs:
            # Revisions are listed newest first, so the last one is the creation
            meta.created_time = datetime(*revs[-1]["timestamp"][:6])
        content = page.text(expandtemplates=not self._no_expand_templates)
        if meta.redirect:
            redirect_pagename = parse_redirect_pagename(content)
            meta.redirect_pagename = PageMeta.normalize_page_name(redirect_pagename)
        return meta, content

    def is_unchanged(self, page: Page) -> bool:
        meta = PageMeta.from_page(page)
        json_path = self._pages_dir / meta.json_filename
        wiki_path = self._pages_dir / meta.wiki_filename

        if not json_path.is_file() or not wiki_path.is_file():
            return False

        try:
            cached = json.loads(json_path.read_text())
        except BaseException as e:
            logger.warning(f"Unreadable cache file: '{str(json_path)}' ({e})")
            return False

        current = serialize(meta)
        assert isinstance(cached, dict)
        assert isinstance(current, dict)

        # 'touched' is also updated when an expanded template changes
        keys = ("revision", "touched")
        return all(cached.get(key) == current.get(key) for key in keys)

    def download_page(self, page: Page, i: int) -> None:
        if self._changed and self.is_unchanged(page):
            logger.debug(f"Unchanged ({i}): {page.name}")
            return

        meta, content = self.page_to_meta(page)
        meta_json = json.dumps(serialize(meta))

        logger.info(f"Download ({i}): {meta.filename}")
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
            if not self._ignore_errors:
                raise

    def download_allpages(self, site: Site) -> Tuple[Set[Path], Set[int]]:
        json_paths = set()
        page_ids = set()
        for i, page in enumerate(site.allpages(namespace=self._namespace), start=1):
            meta = PageMeta.from_page(page)
            json_paths.add(self._pages_dir / meta.json_filename)
            page_ids.add(meta.page_id)
            self.download_page(page, i)
        return json_paths, page_ids

    def prune_pages(self, json_paths: Set[Path], page_ids: Set[int]) -> None:
        for json_path in list(self._pages_dir.rglob("*.json")):
            # Compare as Path objects; 'A://b' and 'A:/b' are the same file
            if json_path in json_paths:
                continue

            try:
                cached = json.loads(json_path.read_text())
                namespace = cached.get("namespace", 0)
                page_id = cached.get("page_id", 0)
            except BaseException as e:
                logger.warning(f"Unreadable cache file: '{str(json_path)}' ({e})")
                continue

            if namespace != self._namespace:
                continue

            # Copies made by the 'index' or 'nav' commands keep the source page id
            if page_id in page_ids:
                continue

            logger.info(f"Prune: {str(json_path.relative_to(self._pages_dir))}")
            wiki_path = Path(str(json_path).removesuffix(".json") + ".wiki")
            json_path.unlink(missing_ok=True)
            wiki_path.unlink(missing_ok=True)

    def request_page(self, site: Site, page_name: str) -> Page:
        try:
            logger.debug(f"Request page: {page_name}")
            page = site.pages[page_name]
        except BaseException as e:
            logger.error(e)
            if not self._ignore_errors:
                raise
        else:
            if isinstance(page, Page):
                return page
            else:
                error_message = f"Unexpected page type: {type(page).__name__}"
                logger.error(error_message)
                if not self._ignore_errors:
                    raise TypeError(error_message)

    def download_pages(self, site: Site, page_names: Sequence[str]) -> None:
        for i, page_name in enumerate(page_names, start=1):
            page = self.request_page(site, page_name)
            self.download_page(page, i)

    def run(self) -> None:
        if not self._endpoint_path:
            raise ValueError("The 'endpoint_path' argument is required")
        if self._namespace not in Site.default_namespaces:
            raise ValueError(f"Unexpected namespace number: {self._namespace}")

        site = self.create_site()

        if self._prune and not self._all:
            raise ValueError("The '--prune' argument requires '--all'")

        if self._all:
            json_paths, page_ids = self.download_allpages(site)
            if self._prune:
                self.prune_pages(json_paths, page_ids)

        if self._pages:
            self.download_pages(site, self._pages)
