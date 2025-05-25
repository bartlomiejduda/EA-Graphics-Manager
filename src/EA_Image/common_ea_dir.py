"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from reversebox.common.logger import get_logger
from reversebox.image.palettes.palette_random import generate_random_palette
from reversebox.image.swizzling.swizzle_ps2 import unswizzle_ps2_palette

from src.EA_Image.attachments.palette_entry import PaletteEntry
from src.EA_Image.constants import PALETTE_TYPES
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import PaletteInfoDTO

logger = get_logger(__name__)


def get_palette_info_dto_from_dir_entry(_ea_dir_entry: DirEntry, ea_image) -> PaletteInfoDTO:
    # try to get palette from binary attachment first
    _palette_data: bytes = b""
    _entry_id: int = 33  # default palette
    _h_default_x_position = -1
    for attachment in _ea_dir_entry.bin_attachments_list:
        if isinstance(attachment, PaletteEntry):
            _palette_data = attachment.raw_data
            _entry_id = attachment.h_record_id
            _h_default_x_position = attachment.h_default_x_position
            break

    if _palette_data and len(_palette_data) > 0:
        if _entry_id in (33, 59) and _h_default_x_position & 0x2000:  # check for palette swizzle flag
            return PaletteInfoDTO(entry_id=_entry_id, data=unswizzle_ps2_palette(_palette_data), swizzle_flag=True)

        return PaletteInfoDTO(
            entry_id=_entry_id, data=_palette_data, swizzle_flag=False
        )  # return palette from binary attachment

    # try to get palette from other dir entry
    for i in range(ea_image.num_of_entries):
        ea_dir_entry = ea_image.dir_entry_list[i]
        if ea_dir_entry.h_record_id in PALETTE_TYPES:
            if (
                ea_dir_entry.h_record_id in (33, 59) and ea_dir_entry.h_default_x_position & 0x2000
            ):  # check for palette swizzle flag
                return PaletteInfoDTO(
                    entry_id=ea_dir_entry.h_record_id,
                    data=unswizzle_ps2_palette(ea_dir_entry.raw_data),
                    swizzle_flag=True,
                )

            return PaletteInfoDTO(
                entry_id=ea_dir_entry.h_record_id, data=ea_dir_entry.raw_data, swizzle_flag=False
            )  # return palette from other dir entry

    logger.warn("Warning! Couldn't find palette data!")
    return PaletteInfoDTO(
        entry_id=_entry_id, data=generate_random_palette(), swizzle_flag=False
    )  # return random palette if no palette has been found
