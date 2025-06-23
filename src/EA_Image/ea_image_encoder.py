"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from PIL import Image
from reversebox.common.common import fill_data_with_padding_to_desired_length
from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.image_encoder import ImageEncoder
from reversebox.image.image_formats import ImageFormats
from reversebox.image.pillow_wrapper import PillowWrapper
from reversebox.image.swizzling.swizzle_ps2 import swizzle_ps2_palette

from src.EA_Image.common import (
    get_bpp_for_image_type,
    get_indexed_image_format,
    get_indexed_palette_format,
)
from src.EA_Image.common_ea_dir import (
    get_palette_info_dto_from_dir_entry,
    handle_image_swizzle_logic,
    is_image_compressed,
    is_image_swizzled,
)
from src.EA_Image.constants import IMPORT_IMAGES_SUPPORTED_TYPES
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import EncodeInfoDTO, PaletteInfoDTO, PartialEncodeInfoDTO
from src.EA_Image.ea_image_decoder import decode_image_data_by_entry_type
from src.EA_Image.ea_image_main import EAImage

logger = get_logger(__name__)


def encode_ea_image(rgba8888_data: bytes, ea_dir: DirEntry, ea_img: EAImage) -> EncodeInfoDTO:
    logger.info("Initializing encode_ea_image")
    entry_type: int = ea_dir.h_record_id
    indexed_image_format: ImageFormats = get_indexed_image_format(get_bpp_for_image_type(entry_type))
    palette_info_dto: PaletteInfoDTO = get_palette_info_dto_from_dir_entry(ea_dir, ea_img)
    palette_format: ImageFormats = get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data))
    final_encoded_image_data: bytes = b""

    if entry_type not in IMPORT_IMAGES_SUPPORTED_TYPES:
        raise Exception("Image type not supported for encoding!")

    partial_main_image_info: PartialEncodeInfoDTO = encode_image_data_by_entry_type(
        entry_type, rgba8888_data, ea_dir.h_width, ea_dir.h_height, indexed_image_format, palette_format
    )
    raw_encoded_image_data: bytes = partial_main_image_info.encoded_image_data

    if is_image_swizzled(ea_dir):
        partial_main_image_info.encoded_image_data = handle_image_swizzle_logic(
            partial_main_image_info.encoded_image_data, entry_type, ea_dir.h_width, ea_dir.h_height, ea_img.sign, True
        )

    final_encoded_image_data += partial_main_image_info.encoded_image_data
    final_encoded_palette_data = partial_main_image_info.encoded_palette_data

    # handle mipmaps
    # TODO - not working! Should be handled by ReverseBox instead?
    decoded_main_tex_data: bytes = decode_image_data_by_entry_type(
        entry_type, raw_encoded_image_data, palette_info_dto, ea_dir
    )
    base_img: Image = PillowWrapper().get_pillow_image_from_rgba8888_data(
        decoded_main_tex_data, ea_dir.h_width, ea_dir.h_height
    )
    mip_width: int = ea_dir.h_width
    mip_height: int = ea_dir.h_height
    for i in range(ea_dir.h_mipmaps_count):
        mip_width //= 2
        mip_height //= 2
        mip_pillow_img: Image = base_img.resize((mip_width, mip_height))
        mip_rgba_data: bytes = PillowWrapper().get_image_data_from_pillow_image(mip_pillow_img)

        partial_mipmap_info: PartialEncodeInfoDTO = encode_image_data_by_entry_type(
            entry_type, mip_rgba_data, mip_width, mip_height, indexed_image_format, palette_format
        )
        partial_mipmap_info.encoded_image_data = handle_image_swizzle_logic(
            partial_mipmap_info.encoded_image_data, entry_type, mip_width, mip_height, ea_img.sign, True
        )

        final_encoded_image_data += partial_mipmap_info.encoded_image_data

    if is_image_compressed(entry_type):
        final_encoded_image_data = RefpackHandler().compress_data(final_encoded_image_data)

    if len(final_encoded_image_data) > len(ea_dir.raw_data):
        raise Exception("Encoded data too big!")

    if len(final_encoded_image_data) < len(ea_dir.raw_data):
        final_encoded_image_data = fill_data_with_padding_to_desired_length(
            final_encoded_image_data, len(ea_dir.raw_data)
        )

    if palette_info_dto.swizzle_flag:
        final_encoded_palette_data = swizzle_ps2_palette(final_encoded_palette_data)

    return EncodeInfoDTO(
        encoded_img_data=final_encoded_image_data,
        encoded_palette_data=final_encoded_palette_data,
        palette_entry_id=palette_info_dto.entry_id,
        is_palette_imported_flag=True if len(final_encoded_palette_data) > 0 else False,
    )


def encode_image_data_by_entry_type(
    entry_type: int,
    rgba8888_data: bytes,
    img_width: int,
    img_height: int,
    indexed_image_format: ImageFormats,
    palette_format: ImageFormats,
) -> PartialEncodeInfoDTO:
    image_encoder = ImageEncoder()
    encoded_palette_data: bytes = b""

    if entry_type == 1:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 2:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 3:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.RGBA5551)
    elif entry_type == 4:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.RGB888)
    elif entry_type == 5:
        encoded_image_data = rgba8888_data
    elif entry_type == 22:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.ARGB8888)
    elif entry_type == 64:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 65:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 66:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.RGBT5551)
    elif entry_type in (88, 89):
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.RGB565)
    elif entry_type == 90:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.RGBX4444)
    elif entry_type == 91:
        encoded_image_data = rgba8888_data
    elif entry_type == 92:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 93:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 96:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC1_DXT1
        )
    elif entry_type == 97:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC2_DXT3
        )
    elif entry_type == 98:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC3_DXT5
        )
    elif entry_type == 109:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.BGRA4444)
    elif entry_type == 120:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.BGR565)
    elif entry_type == 121:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=16
        )
    elif entry_type == 123:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data, img_width, img_height, indexed_image_format, palette_format, max_color_count=256
        )
    elif entry_type == 125:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.BGRA8888)
    elif entry_type == 126:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.BGRA5551)
    elif entry_type == 127:
        encoded_image_data = image_encoder.encode_image(rgba8888_data, img_width, img_height, ImageFormats.BGR888)
    else:
        raise Exception("Image type not supported for encoding!")

    return PartialEncodeInfoDTO(encoded_image_data=encoded_image_data, encoded_palette_data=encoded_palette_data)
