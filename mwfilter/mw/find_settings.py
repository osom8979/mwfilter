# -*- coding: utf-8 -*-

from typing import List, Optional

from mwfilter.mw.convert_info import ConvertInfo, find_convert_info
from mwfilter.mw.settings import Settings


def find_settings(infos: List[ConvertInfo], settings_page: str) -> Optional[Settings]:
    try:
        settings_info = find_convert_info(infos, settings_page)
        return Settings.from_convert_info(settings_info.text)
    except:  # noqa
        return None
