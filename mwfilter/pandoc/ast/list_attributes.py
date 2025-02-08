# -*- coding: utf-8 -*-

from dataclasses import dataclass

from mwfilter.pandoc.ast.enums import ListNumberDelim, ListNumberStyle


@dataclass
class ListAttributes:
    """
    List attributes.
    The first element of the triple is the start number of the list.
    """

    start_number: int = 0
    list_number_style: ListNumberStyle = ListNumberStyle.DefaultStyle
    list_number_delim: ListNumberDelim = ListNumberDelim.DefaultDelim

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, list)
        assert len(e) == 3
        start_number = e[0]
        assert isinstance(start_number, int)
        list_number_style = ListNumberStyle.parse_object(e[1])
        list_number_delim = ListNumberDelim.parse_object(e[2])
        return cls(start_number, list_number_style, list_number_delim)
