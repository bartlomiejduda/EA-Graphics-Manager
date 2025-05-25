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


@dataclass
class EncodeInfoDTO:
    encoded_img_data: bytes
    encoded_palette_data: bytes
    palette_entry_id: int
    is_palette_imported_flag: bool
