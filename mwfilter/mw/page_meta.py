# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from mwclient.page import Page


def pagename_to_filename(pagename: str) -> str:
    return pagename.removeprefix("/").replace(" ", "_")


@dataclass
class PageMeta:
    filename: str = field(default_factory=str)
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
            filename=pagename_to_filename(page.name),
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
