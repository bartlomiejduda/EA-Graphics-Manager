"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from reversebox.common.logger import get_logger
from reversebox.image.image_formats import ImageFormats

# fmt: off

logger = get_logger(__name__)


def get_bpp_for_image_type(ea_img_type: int) -> int:
    if ea_img_type == 0x44:
        return 1
    elif ea_img_type in (0x01, 0x10, 0x18, 0x1E, 0x40, 0x5C, 0x60, 0x63, 0x79, 0x7A):
        return 4
    elif ea_img_type in (0x02, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x11, 0x12, 0x19, 0x41, 0x5D, 0x61, 0x62, 0x64, 0x7B):
        return 8
    elif ea_img_type in (0x1C, 0x6C):
        return 12
    elif ea_img_type in (0x03, 0x15, 0x20, 0x32, 0x39, 0x59, 0x7E):
        return 15
    elif ea_img_type in (0x13, 0x14, 0x1A, 0x23, 0x27, 0x28, 0x29, 0x2D, 0x30, 0x31, 0x38, 0x3A, 0x42, 0x58, 0x5A, 0x65, 0x67, 0x68, 0x6D, 0x78):
        return 16
    elif ea_img_type in (0x04, 0x22, 0x24, 0x43, 0x66, 0x7F):
        return 24
    elif ea_img_type in (0x05, 0x16, 0x21, 0x2A, 0x2C, 0x2E, 0x3B, 0x5B, 0x6A, 0x7D):
        return 32
    else:
        logger.warning(f"Image type {str(ea_img_type)} not supported! Can't get bpp info!")
        return 8  # default bpp


def get_indexed_image_format(bpp: int) -> ImageFormats:
    if bpp == 4:
        return ImageFormats.PAL4
    elif bpp == 8:
        return ImageFormats.PAL8
    elif bpp == 16:
        return ImageFormats.PAL16
    elif bpp == 32:
        return ImageFormats.PAL32
    else:
        logger.warning(f"Image format not found for bpp={bpp}")
        return ImageFormats.PAL8  # default


def get_indexed_palette_format(palette_entry_id: int, palette_size: int) -> ImageFormats:

    if palette_entry_id == 33:
        return ImageFormats.RGBA8888
    elif palette_entry_id == 34:
        return ImageFormats.RGBX6666  # TODO
    elif palette_entry_id == 35:
        return ImageFormats.RGBX5551
    elif palette_entry_id == 36:
        return ImageFormats.RGB888
    elif palette_entry_id == 41:
        return ImageFormats.RGB565
    elif palette_entry_id == 42:  # TODO - check RGB/BGR logic
        return ImageFormats.BGRA8888 if palette_size == 1024 else ImageFormats.BGR888
    elif palette_entry_id == 45:
        return ImageFormats.XRGB1555  # TODO - check if format is ok
    elif palette_entry_id == 50:
        return ImageFormats.N64_BGR5A3
    elif palette_entry_id == 58:
        return ImageFormats.RGBA8888  # TODO - check if format is ok
    elif palette_entry_id == 59:
        return ImageFormats.RGBA8888
    else:
        logger.warning(f"Palette ID={palette_entry_id} not supported!")

    logger.warning(f"Palette format has not been found for palette_id={palette_entry_id}")
    return ImageFormats.RGB565  # default
