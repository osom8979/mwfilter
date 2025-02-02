# -*- coding: utf-8 -*-

import json
import os
import pickle
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from glob import glob
from io import StringIO
from logging import INFO, NOTSET, Formatter, StreamHandler, getLogger
from pathlib import Path
from re import Pattern
from re import compile as re_compile
from sys import exit as sys_exit
from sys import stderr, stdout
from typing import Any, Dict, List, Optional

from mwclient import Site
from mwclient.page import Page
from pypandoc import convert_file, convert_text
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
    namespace: int = 0
    name: str = field(default_factory=str)
    page_title: str = field(default_factory=str)
    base_title: str = field(default_factory=str)
    base_name: str = field(default_factory=str)
    touched: datetime = datetime.now()
    revision: int = 0
    exists: bool = False
    length: int = 0
    redirect: bool = False
    page_id: int = 0
    protection: Dict[Any, Any] = field(default_factory=dict)
    content_model: str = field(default_factory=str)
    page_language: str = field(default_factory=str)
    restriction_types: List[str] = field(default_factory=list)
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


@dataclass
class ConvertInfo:
    meta_path: str = str()
    text_path: str = str()
    meta: PageMeta = field(default_factory=lambda: PageMeta())
    text: str = str()

    @classmethod
    def from_paths(cls, meta_path: Path, text_path: Path):
        return cls(
            meta_path=str(meta_path),
            text_path=str(text_path),
            meta=deserialize(json.loads(meta_path.read_bytes()), PageMeta),
            text=text_path.read_text(),
        )

    @property
    def title(self):
        return self.meta.name

    @property
    def filename(self):
        return self.meta.name.removeprefix("/")

    @property
    def date(self):
        return self.meta.touched.date().isoformat()

    @property
    def url_title(self):
        return urllib.parse.quote(self.title)

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
            self.text_path,
            to="markdown",
            format="mediawiki",
        )


@dataclass
class MwSettings:
    allow_pages: List[str] = field(default_factory=list)
    allow_patterns: List[Pattern[str]] = field(default_factory=list)
    deny_pages: List[str] = field(default_factory=list)
    deny_patterns: List[Pattern[str]] = field(default_factory=list)

    @classmethod
    def from_convert_info(cls, info: ConvertInfo):
        info_json = convert_text(info.text, to="json", format="mediawiki")
        info_obj = json.loads(info_json)
        assert isinstance(info_obj, dict)
        blocks = info_obj["blocks"]
        assert isinstance(blocks, list)

        allow_pages: List[str] = list()
        allow_patterns: List[str] = list()
        deny_pages: List[str] = list()
        deny_patterns: List[str] = list()

        option_cursor: Optional[List[str]] = None

        for block in blocks:
            assert isinstance(block, dict)
            t = block["t"]
            c = block["c"]
            assert isinstance(t, str)
            assert isinstance(c, list)
            if t == "Header":
                header_keyname = c[1][0]
                assert isinstance(header_keyname, str)
                assert header_keyname.islower()
                match header_keyname:
                    case "allowpages":
                        option_cursor = allow_pages
                    case "allowpatterns":
                        option_cursor = allow_patterns
                    case "denypages":
                        option_cursor = deny_pages
                    case "denypatterns":
                        option_cursor = deny_patterns
                    case _:
                        option_cursor = None
            elif t == "BulletList":
                if option_cursor is not None:
                    for item in c:
                        assert isinstance(item, list)
                        assert len(item) == 1
                        it = item[0]["t"]
                        ic = item[0]["c"]
                        assert isinstance(it, str)
                        assert isinstance(ic, list)
                        ic0 = ic[0]
                        assert isinstance(ic0, dict)
                        ic0t = ic0["t"]
                        ic0c = ic0["c"]
                        assert isinstance(ic0t, str)
                        assert isinstance(ic0c, str)
                        if ic0t == "Str":
                            option_cursor.append(ic0c)
            else:
                option_cursor = None

        return cls(
            allow_pages=allow_pages,
            allow_patterns=[re_compile(p) for p in allow_patterns],
            deny_pages=deny_pages,
            deny_patterns=[re_compile(p) for p in deny_patterns],
        )

    def filter(self, info: ConvertInfo) -> bool:
        if self.allow_pages and info.title in self.allow_pages:
            return True

        if self.allow_patterns:
            for pattern in self.deny_patterns:
                if pattern.match(info.title) is not None:
                    return True

        if self.deny_pages and info.title in self.deny_pages:
            return False

        if self.deny_patterns:
            for pattern in self.deny_patterns:
                if pattern.match(info.title) is not None:
                    return False

        return True


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
                    meta_data = json.dumps(meta_obj)
                    meta_path.write_text(meta_data)
                if not text_path.is_file():
                    text = page.text()
                    text_path.write_text(text)
                progress_bar.write(title)
            finally:
                progress_bar.update()


def create_convert_infos(cache: str, *, use_picking=False) -> List[ConvertInfo]:
    result = list()
    meta_filenames = glob("*.json", root_dir=cache)
    meta_filenames.sort()
    with tqdm(total=len(meta_filenames)) as progress_bar:
        for meta_filename in meta_filenames:
            page_id = os.path.splitext(meta_filename)[0]
            try:
                meta_path = Path(cache) / meta_filename
                text_path = Path(cache) / f"{page_id}.wiki"
                info_path = Path(cache) / f"{page_id}.info"

                if info_path.is_file():
                    info = pickle.loads(info_path.read_bytes())
                else:
                    info = ConvertInfo.from_paths(meta_path, text_path)
                    if use_picking:
                        info_path.write_bytes(pickle.dumps(info))

                result.append(info)
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
        logger.info("Skip download step")
    else:
        logger.info("Start download step ...")
        download_pages(cache, hostname, password, username)

    logger.info("Read all cached pages ...")
    infos = create_convert_infos(cache)

    settings = find_settings(infos, settings_page)
    infos = list(filter(lambda i: settings.filter(i), infos))

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
