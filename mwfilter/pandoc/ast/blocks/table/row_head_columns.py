# -*- coding: utf-8 -*-


class RowHeadColumns(int):
    """
    The number of columns taken up by the row head of each row of a TableBody.
    The row body takes up the remaining columns.
    """

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, int)
        return cls(e)
