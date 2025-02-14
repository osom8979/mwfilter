# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from mwclient import Site
from mwclient.page import Page

from mwfilter.mw.namespace import FILE_NAMESPACE, TEMPLATE_NAMESPACE


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

    method_version: Optional[int] = None
    redirect_pagename: Optional[str] = None
    authors: List[str] = field(default_factory=list)

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

    @property
    def page_name(self) -> str:
        if self.namespace in (FILE_NAMESPACE, TEMPLATE_NAMESPACE):
            default_namespace = Site.default_namespaces[self.namespace]
            return f"{default_namespace}:{self.page_title}"
        else:
            return self.name

    @staticmethod
    def normalize_page_name(page_name: str) -> str:
        return page_name.removeprefix("/").replace(" ", "_")

    @property
    def filename(self) -> str:
        return self.normalize_page_name(self.page_name)

    @property
    def date(self):
        return self.touched.date().isoformat()

    @property
    def json_filename(self) -> str:
        return self.filename + ".json"

    @property
    def wiki_filename(self) -> str:
        return self.filename + ".wiki"

    @property
    def markdown_filename(self) -> str:
        return self.filename + ".md"
