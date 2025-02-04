# -*- coding: utf-8 -*-

from typing import List, Optional

from mwfilter.mw.convert_info import ConvertInfo, find_convert_info
from mwfilter.mw.settings import Settings


def find_settings(
    infos: List[ConvertInfo],
    settings_page: Optional[str] = None,
    *,
    default: Optional[Settings] = None,
) -> Optional[Settings]:
    if settings_page:
        try:
            settings_info = find_convert_info(infos, settings_page)
            return Settings.from_convert_info(settings_info.text)
        except:  # noqa
            pass
    return default
