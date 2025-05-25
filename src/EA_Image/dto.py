"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from dataclasses import dataclass


@dataclass
class PaletteInfoDTO:
    entry_id: int
    data: bytes
    swizzle_flag: bool
