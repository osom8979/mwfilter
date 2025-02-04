# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwclient import Site


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


def request_statistics(site: Site) -> Statistics:
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


def request_all_pages_count(site: Site) -> int:
    return request_statistics(site).pages
