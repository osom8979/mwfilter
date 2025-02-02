# -*- coding: utf-8 -*-

import os
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from glob import glob
from io import StringIO
from json import dumps, loads
from logging import INFO, NOTSET, Formatter, StreamHandler, getLogger
from pathlib import Path
from sys import exit as sys_exit
from sys import stderr, stdout
from typing import Any, Dict, List, Optional

from mwclient import Site
from mwclient.page import Page
from pypandoc import convert_file
from tqdm import tqdm
from type_serialize import deserialize, serialize

from mwfilter.arguments import get_default_arguments


@dataclass
class Statistics:
    pages: int
    articles: int
    edits: int
    images: int
    users: int
    active_users: int
    admins: int
    jobs: int


@dataclass
class PageMeta:
    namespace: int
    name: str
    page_title: str
    base_title: str
    base_name: str
    touched: datetime
    revision: int
    exists: bool
    length: int
    redirect: bool
    page_id: int
    protection: Dict[Any, Any]
    content_model: str
    page_language: str
    restriction_types: List[str]
    edit_time: Optional[datetime] = None
    last_rev_time: Optional[datetime] = None

    @classmethod
    def from_page(cls, page: Page):
        return cls(
            namespace=page.namespace,
            name=page.name,
            page_title=page.page_title,
            base_title=page.base_title,
            base_name=page.base_name,
            touched=datetime(*page.touched[:6]),
            revision=page.revision,
            exists=page.exists,
            length=page.length,
            redirect=page.redirect,
            page_id=page.pageid,
            protection=page.protection,
            content_model=page.contentmodel,
            page_language=page.pagelanguage,
            restriction_types=page.restrictiontypes,
            edit_time=page.edit_time,
            last_rev_time=page.last_rev_time,
        )


class ConvertInfo:
    _meta: PageMeta

    def __init__(self, meta_path: Path, text_path: Path):
        self._meta_path = meta_path
        self._text_path = text_path
        self._meta = deserialize(loads(self._meta_path.read_bytes()), PageMeta)
        self._text = self._text_path.read_text()

    @property
    def title(self):
        return self._meta.name

    @property
    def filename(self):
        return self._meta.name.removeprefix("/")

    @property
    def date(self):
        return self._meta.touched.date().isoformat()

    @property
    def url_title(self):
        return urllib.parse.quote(self.title)

    @property
    def text(self):
        return self._text

    @property
    def yaml_frontmatter(self):
        buffer = StringIO()
        buffer.write("---\n")
        buffer.write(f"title: {self.title}\n")
        buffer.write(f"date: {self.date}\n")
        buffer.write("---\n")
        buffer.write("\n")
        return buffer.getvalue()

    def as_markdown(self) -> str:
        return self.yaml_frontmatter + convert_file(
            self._text_path,
            to="markdown",
            format="mediawiki",
        )


@dataclass
class MwSettings:
    @classmethod
    def from_convert_info(cls, info: ConvertInfo):
        # info_content = info.text
        # TODO: parse info_content
        return cls()


def silent_unnecessary_loggers() -> None:
    import pypandoc

    pypandoc.logger.setLevel(NOTSET)

    getLogger("pandoc").setLevel(NOTSET)
    getLogger("urllib3").setLevel(NOTSET)


def default_logger():
    logger = getLogger()
    formatter = Formatter("{levelname[0]} {asctime} {name} {message}", style="{")
    handler = StreamHandler(stdout)
    handler.setFormatter(formatter)
    logger.setLevel(INFO)
    logger.addHandler(handler)
    return logger


def request_statistics(site: Site):
    response = site.api("query", meta="siteinfo", siprop="statistics")
    statistics = response["query"]["statistics"]
    return Statistics(
        pages=statistics["pages"],
        articles=statistics["articles"],
        edits=statistics["edits"],
        images=statistics["images"],
        users=statistics["users"],
        active_users=statistics["activeusers"],
        admins=statistics["admins"],
        jobs=statistics["jobs"],
    )


def request_all_pages_count(site: Site):
    return request_statistics(site).pages


def download_pages(
    cache: str,
    hostname: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    path="/",
) -> None:
    site = Site(hostname, path=path)

    if username and password:
        site.login(username, password)

    with tqdm(total=request_all_pages_count(site)) as progress_bar:
        for page in site.allpages():
            try:
                assert isinstance(page, Page)
                title = page.name
                page_id = page.pageid
                meta_path = Path(cache) / f"{page_id}.json"
                text_path = Path(cache) / f"{page_id}.wiki"
                if not meta_path.is_file():
                    meta = PageMeta.from_page(page)
                    meta_obj = serialize(meta)
                    meta_data = dumps(meta_obj)
                    meta_path.write_text(meta_data)
                if not text_path.is_file():
                    text = page.text()
                    text_path.write_text(text)
                progress_bar.write(title)
            finally:
                progress_bar.update()


def create_convert_infos(cache: str) -> List[ConvertInfo]:
    result = list()
    meta_filenames = glob("*.json", root_dir=cache)
    meta_filenames.sort()
    with tqdm(total=len(meta_filenames)) as progress_bar:
        for meta_filename in meta_filenames:
            page_id = os.path.splitext(meta_filename)[0]
            try:
                meta_path = Path(cache) / meta_filename
                text_path = Path(cache) / f"{page_id}.wiki"
                result.append(ConvertInfo(meta_path, text_path))
            finally:
                progress_bar.update()
    return result


def find_settings_info(infos: List[ConvertInfo], settings_page: str) -> ConvertInfo:
    for info in infos:
        if info.title == settings_page:
            return info
    raise IndexError("Not found settings page")


def find_settings(infos: List[ConvertInfo], settings_page: Optional[str]) -> MwSettings:
    if settings_page:
        try:
            settings_info = find_settings_info(infos, settings_page)
            return MwSettings.from_convert_info(settings_info)
        except:  # noqa
            pass
    return MwSettings()


def app(
    hostname: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    output: Optional[str] = None,
    cache: Optional[str] = None,
    settings_page: Optional[str] = None,
    skip_download=False,
) -> None:
    if not hostname:
        raise ValueError("The 'url' argument is required")
    if not output:
        raise ValueError("The 'output' argument is required")
    if not cache:
        raise ValueError("The 'cache' argument is required")

    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    if not os.path.exists(cache):
        os.makedirs(cache, exist_ok=True)

    if not os.path.isdir(cache):
        raise NotADirectoryError("Cache directory is not a directory")
    if not os.path.isdir(output):
        raise NotADirectoryError("Output directory is not a directory")

    silent_unnecessary_loggers()
    logger = default_logger()

    if skip_download:
        logger.debug("Skip download step")
    else:
        logger.info("Start download step ...")
        download_pages(cache, hostname, password, username)

    logger.info("Read all cached pages ...")
    infos = create_convert_infos(cache)

    # settings = find_settings(infos, settings_page)

    logger.info("Write all output pages ...")
    with tqdm(total=len(infos)) as progress_bar:
        for info in infos:
            try:
                output_path = Path(output) / f"{info.filename}.md"
                if output_path.is_file():
                    continue
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(info.as_markdown())
            finally:
                progress_bar.update()


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)
    try:
        app(
            hostname=args.hostname,
            username=args.username,
            password=args.password,
            output=args.output,
            cache=args.cache,
            settings_page=args.settings_page,
            skip_download=args.skip_download,
        )
    except BaseException as e:
        print(e, file=stderr)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys_exit(main())
