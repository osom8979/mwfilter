# -*- coding: utf-8 -*-

from typing import Final


class ColWidth(float):
    """The width of a table column, as a percentage of the text width."""

    DEFAULT: Final[float] = 0.0

    @classmethod
    def parse_object(cls, e):
        assert isinstance(e, dict)
        if e["t"] == "ColWidthDefault":
            return cls(0.0)
        elif e["t"] == "ColWidth":
            assert isinstance(e["c"], float)
            return cls(e["c"])
        else:
            raise ValueError(f"Unexpected element type: {e}")

    @property
    def is_default(self):
        return self == self.DEFAULT
