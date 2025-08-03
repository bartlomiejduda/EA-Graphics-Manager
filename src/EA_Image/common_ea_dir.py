"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import traceback

from reversebox.common.logger import get_logger
from reversebox.image.swizzling.swizzle_gamecube import (
    swizzle_gamecube,
    unswizzle_gamecube,
)
from reversebox.image.swizzling.swizzle_morton import swizzle_morton, unswizzle_morton
from reversebox.image.swizzling.swizzle_ps2 import (
    swizzle_ps2,
    unswizzle_ps2,
    unswizzle_ps2_palette,
)
from reversebox.image.swizzling.swizzle_psp import swizzle_psp, unswizzle_psp

from src.EA_Image.attachments.palette_entry import PaletteEntry
from src.EA_Image.common import get_bpp_for_image_type
from src.EA_Image.constants import PALETTE_TYPES
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import PaletteInfoDTO
from src.EA_Image.ea_default_palette import ea_default_palette_data

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
        entry_id=_entry_id, data=bytes(ea_default_palette_data), swizzle_flag=False
    )  # return default palette if no palette has been found


def is_image_swizzled(ea_dir_entry: DirEntry) -> bool:
    if ea_dir_entry.h_flag2_swizzled or ea_dir_entry.new_shape_flag_swizzled:
        return True
    return False


def is_image_compressed(entry_type: int) -> bool:
    compression_flag: int = entry_type & 0x80  # 0 - not compressed / 128 - compressed
    if compression_flag == 128:
        return True
    return False


def handle_image_swizzle_logic(
    image_data: bytes, entry_type: int, img_width: int, img_height: int, ea_img_signature: str, swizzle_flag: bool
) -> bytes:
    try:
        if entry_type >= 8 and entry_type <= 15:  # for PS2 games (GST textures)
            pass  # swizzling handled by GST decoder
        elif entry_type == 30:  # for WII games (DXT1/CMPR textures)
            pass  # swizzling handled by N64 decoder
        elif ea_img_signature in ("SHPX", "ShpX", "SHPI", "ShpF"):  # for XBOX and PC games
            if not swizzle_flag:
                image_data = unswizzle_morton(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
            else:
                image_data = swizzle_morton(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
        elif ea_img_signature in ("SHPM", "ShpM"):  # for PSP games
            if not swizzle_flag:
                image_data = unswizzle_psp(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
            else:
                image_data = swizzle_psp(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
        elif ea_img_signature in ("SHPS", "ShpS") and (
            entry_type < 8 or entry_type > 15
        ):  # for PS2 games (standard textures)
            bpp = get_bpp_for_image_type(entry_type)
            if bpp in (4, 8, 15, 16):
                if not swizzle_flag:
                    image_data = unswizzle_ps2(image_data, img_width, img_height, bpp, swizzle_type=1)
                else:
                    image_data = swizzle_ps2(image_data, img_width, img_height, bpp, swizzle_type=1)
            else:
                logger.warning(f"PS2 unswizzle for bpp {bpp} is not supported yet!")
        elif ea_img_signature in ("SHPG", "ShpG"):  # for WII/GameCube games
            if not swizzle_flag:
                image_data = unswizzle_gamecube(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
            else:
                image_data = swizzle_gamecube(image_data, img_width, img_height, get_bpp_for_image_type(entry_type))
        else:
            logger.warning(f"Swizzling for signature {ea_img_signature} is not supported yet!")
    except Exception as error:
        logger.error(f"Error while unswizzling images! Error: {error}")
        logger.error(traceback.format_exc())

    return image_data
