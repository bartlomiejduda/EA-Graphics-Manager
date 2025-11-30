"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from typing import Optional

from reversebox.common.logger import get_logger
from reversebox.image.image_decoder import ImageDecoder
from reversebox.image.image_formats import ImageFormats

from src.EA_Image.common import (
    get_bpp_for_image_type,
    get_indexed_image_format,
    get_indexed_palette_format,
)
from src.EA_Image.common_ea_dir import is_image_swizzled
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import PaletteInfoDTO

logger = get_logger(__name__)


def decode_image_data_by_entry_type(
    entry_type: int, image_data: bytes, palette_info_dto: PaletteInfoDTO, ea_dir_entry: DirEntry
) -> Optional[bytes]:
    ea_image_decoder: ImageDecoder = ImageDecoder()

    if entry_type == 1:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 2:

        if len(palette_info_dto.data) == 0:
            logger.error("Error while converting palette data for type 2!")
            return

        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 3:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBA5551
        )
    elif entry_type == 4:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
        )
    elif entry_type == 5:
        return image_data  # r8g8b8a8
    elif entry_type == 8:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST121,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 9:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST221,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 10:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST421,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 11:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST821,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 12:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST122,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 13:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST222,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 14:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST422,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 15:
        return ea_image_decoder.decode_gst_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.GST822,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            is_swizzled=is_image_swizzled(ea_dir_entry),
        )
    elif entry_type == 20:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565, image_endianess="big"
        )
    elif entry_type == 22:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB8888
        )
    elif entry_type == 24:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            palette_endianess="big",
        )
    elif entry_type == 25:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            palette_endianess="big",
        )
    elif entry_type == 30:
        return ea_image_decoder.decode_n64_image(
            image_data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.N64_CMPR,
        )
    elif entry_type == 33:
        return image_data  # palette
    elif entry_type == 34:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
        )  # palette
    elif entry_type == 35:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
        )  # palette
    elif entry_type == 36:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
        )  # palette
    elif entry_type == 42:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBA8888
        )  # palette
    elif entry_type == 59:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
        )  # palette
    elif entry_type == 64:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 65:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 66:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBT5551
        )
    elif entry_type == 67:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
        )
    elif entry_type == 88:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
        )
    elif entry_type == 89:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
        )
    elif entry_type == 90:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBX4444
        )
    elif entry_type == 91:
        return image_data  # r8g8b8a8
    elif entry_type == 92:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 93:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 96:
        return ea_image_decoder.decode_compressed_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BC1_DXT1
        )
    elif entry_type == 97:
        return ea_image_decoder.decode_compressed_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BC2_DXT3
        )
    elif entry_type == 98:
        return ea_image_decoder.decode_compressed_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BC3_DXT5
        )
    elif entry_type == 100:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.GRAY8
        )
    elif entry_type == 101:
        return ea_image_decoder.decode_n64_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.N64_IA8
        )
    elif entry_type == 104:
        return ea_image_decoder.decode_yuv_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.YUV422_YUY2
        )
    elif entry_type == 109:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGRA4444
        )
    elif entry_type == 115:
        return ea_image_decoder.decode_indexed_image(
            image_data[1024:],
            image_data[:1024],
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.PAL8,
            ImageFormats.RGBA8888,
        )
    elif entry_type == 119:
        return ea_image_decoder.decode_indexed_image(
            image_data[64:],
            image_data[:64],
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            ImageFormats.PAL4,
            ImageFormats.RGBA8888,
        )
    elif entry_type == 120:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGR565
        )
    elif entry_type == 121:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 122:
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
            image_endianess="big",
        )
    elif entry_type == 123:
        # for i in range(1024):
        #     palette_data += b"\x00"  # workaround for Need For Speed 2 PC, e.g. "TR000_QFS.fsh"
        return ea_image_decoder.decode_indexed_image(
            image_data,
            palette_info_dto.data,
            ea_dir_entry.h_width,
            ea_dir_entry.h_height,
            get_indexed_image_format(get_bpp_for_image_type(entry_type)),
            get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data)),
        )
    elif entry_type == 125:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGRA8888
        )
    elif entry_type == 126:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGRA5551
        )
    elif entry_type == 127:
        return ea_image_decoder.decode_image(
            image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGR888
        )
    else:
        logger.error(f"Unsupported type {entry_type} for convert and preview!")
        return
