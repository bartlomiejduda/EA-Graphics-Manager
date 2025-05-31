"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from reversebox.common.common import fill_data_with_padding_to_desired_length
from reversebox.common.logger import get_logger
from reversebox.image.image_encoder import ImageEncoder
from reversebox.image.image_formats import ImageFormats
from reversebox.image.swizzling.swizzle_ps2 import swizzle_ps2_palette

from src.EA_Image.common import (
    get_bpp_for_image_type,
    get_indexed_image_format,
    get_indexed_palette_format,
)
from src.EA_Image.common_ea_dir import (
    get_palette_info_dto_from_dir_entry,
    handle_image_swizzle_logic,
    is_image_swizzled,
)
from src.EA_Image.constants import IMPORT_IMAGES_SUPPORTED_TYPES
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import EncodeInfoDTO, PaletteInfoDTO
from src.EA_Image.ea_image_main import EAImage

logger = get_logger(__name__)


def encode_ea_image(rgba8888_data: bytes, ea_dir: DirEntry, ea_img: EAImage) -> EncodeInfoDTO:
    logger.info("Initializing encode_ea_image")
    entry_type: int = ea_dir.h_record_id
    encoded_palette_data: bytes = b""
    image_encoder = ImageEncoder()

    if entry_type not in IMPORT_IMAGES_SUPPORTED_TYPES:
        raise Exception("Image type not supported for encoding!")

    indexed_image_format: ImageFormats = get_indexed_image_format(get_bpp_for_image_type(entry_type))
    palette_info_dto: PaletteInfoDTO = get_palette_info_dto_from_dir_entry(ea_dir, ea_img)
    palette_format: ImageFormats = get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data))

    if entry_type == 1:  # TODO - MIPMAPS!!!!!
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 2:  # TODO - MIPMAPS!!!!!
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 3:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.RGBA5551
        )
    elif entry_type == 4:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.RGB888
        )
    elif entry_type == 5:
        encoded_image_data = rgba8888_data
    elif entry_type == 22:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.ARGB8888
        )
    elif entry_type == 64:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 65:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 66:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.RGBT5551
        )
    elif entry_type in (88, 89):
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.RGB565
        )
    elif entry_type == 90:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.RGBX4444
        )
    elif entry_type == 91:
        encoded_image_data = rgba8888_data
    elif entry_type == 92:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 93:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 96:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BC1_DXT1
        )
    elif entry_type == 97:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BC2_DXT3
        )
    elif entry_type == 98:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BC3_DXT5
        )
    elif entry_type == 109:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BGRA4444
        )
    elif entry_type == 120:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BGR565
        )
    elif entry_type == 121:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 123:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 125:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BGRA8888
        )
    elif entry_type == 126:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BGRA5551
        )
    elif entry_type == 127:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.BGR888
        )
    else:
        raise Exception("Image type not supported for encoding!")

    if is_image_swizzled(ea_dir):
        encoded_image_data = handle_image_swizzle_logic(encoded_image_data, entry_type, ea_dir, ea_img.sign, True)

    if len(encoded_image_data) < len(ea_dir.raw_data):  # TODO - remove this after implementing support for mipmaps
        encoded_image_data = fill_data_with_padding_to_desired_length(encoded_image_data, len(ea_dir.raw_data))

    if palette_info_dto.swizzle_flag:
        encoded_palette_data = swizzle_ps2_palette(encoded_palette_data)

    return EncodeInfoDTO(
        encoded_img_data=encoded_image_data,
        encoded_palette_data=encoded_palette_data,
        palette_entry_id=palette_info_dto.entry_id,
        is_palette_imported_flag=True if len(encoded_palette_data) > 0 else False,
    )
