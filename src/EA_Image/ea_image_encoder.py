"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import PIL.Image
from reversebox.common.common import fill_data_with_padding_to_desired_length
from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.common import get_linear_image_data_size
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
    is_image_compressed,
    is_image_swizzled,
)
from src.EA_Image.constants import (
    IMPORT_IMAGES_SUPPORTED_TYPES,
    mipmaps_resampling_mapping,
)
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import EncodeInfoDTO, PaletteInfoDTO, PartialEncodeInfoDTO
from src.EA_Image.ea_image_main import EAImage

logger = get_logger(__name__)


def encode_ea_image(rgba8888_data: bytes, ea_dir: DirEntry, ea_img: EAImage, gui_main) -> EncodeInfoDTO:
    logger.info("Initializing encode_ea_image")
    entry_type: int = ea_dir.h_record_id & 0x7F
    indexed_image_format: ImageFormats = get_indexed_image_format(get_bpp_for_image_type(entry_type))
    palette_info_dto: PaletteInfoDTO = get_palette_info_dto_from_dir_entry(ea_dir, ea_img)
    palette_format: ImageFormats = get_indexed_palette_format(palette_info_dto.entry_id, len(palette_info_dto.data))
    mipmaps_resampling_type_str: str = gui_main.current_mipmaps_resampling.get()
    mipmaps_resampling_type: PIL.Image.Resampling = mipmaps_resampling_mapping[mipmaps_resampling_type_str]

    if entry_type not in IMPORT_IMAGES_SUPPORTED_TYPES:
        raise Exception("Image type not supported for encoding!")

    # encode logic (main + mipmaps)
    partial_image_info: PartialEncodeInfoDTO = encode_image_data_by_entry_type(
        entry_type,
        rgba8888_data,
        ea_dir.h_width,
        ea_dir.h_height,
        indexed_image_format,
        palette_format,
        ea_dir.h_mipmaps_count if isinstance(ea_dir.h_mipmaps_count, int) else ea_dir.new_shape_number_of_mipmaps,
        mipmaps_resampling_type,
    )

    # swizzle logic
    if is_image_swizzled(ea_dir):
        start_offset: int = 0
        image_size: int = get_linear_image_data_size(ea_dir.h_image_bpp, ea_dir.h_width, ea_dir.h_height)
        end_offset: int = image_size
        swizzled_image_data = handle_image_swizzle_logic(
            partial_image_info.encoded_image_data[start_offset:end_offset],
            entry_type,
            ea_dir.h_width,
            ea_dir.h_height,
            ea_img.sign,
            True,
        )

        # mipmaps swizzle logic
        if ea_dir.h_mipmaps_count and ea_dir.h_mipmaps_count > 0:
            mip_width: int = ea_dir.h_width
            mip_height: int = ea_dir.h_height
            for i in range(ea_dir.h_mipmaps_count):
                mip_width //= 2
                mip_height //= 2
                mipmap_size = get_linear_image_data_size(ea_dir.h_image_bpp, mip_width, mip_height)
                start_offset = end_offset
                end_offset = start_offset + mipmap_size

                mip_swizzled_data = handle_image_swizzle_logic(
                    partial_image_info.encoded_image_data[start_offset:end_offset],
                    entry_type,
                    mip_width,
                    mip_height,
                    ea_img.sign,
                    True,
                )
                swizzled_image_data += mip_swizzled_data

        partial_image_info.encoded_image_data = swizzled_image_data

    # compression logic
    if is_image_compressed(entry_type):
        partial_image_info.encoded_image_data = RefpackHandler().compress_data(partial_image_info.encoded_image_data)

    if len(partial_image_info.encoded_image_data) > len(ea_dir.raw_data):
        raise Exception("Encoded data too big!")

    if len(partial_image_info.encoded_image_data) < len(ea_dir.raw_data):
        partial_image_info.encoded_image_data = fill_data_with_padding_to_desired_length(
            partial_image_info.encoded_image_data, len(ea_dir.raw_data)
        )

    if palette_info_dto.swizzle_flag:
        partial_image_info.encoded_palette_data = swizzle_ps2_palette(partial_image_info.encoded_palette_data)

    return EncodeInfoDTO(
        encoded_img_data=partial_image_info.encoded_image_data,
        encoded_palette_data=partial_image_info.encoded_palette_data,
        palette_entry_id=palette_info_dto.entry_id,
        is_palette_imported_flag=True if len(partial_image_info.encoded_palette_data) > 0 else False,
    )


def encode_image_data_by_entry_type(
    entry_type: int,
    rgba8888_data: bytes,
    img_width: int,
    img_height: int,
    indexed_image_format: ImageFormats,
    palette_format: ImageFormats,
    mipmaps_count: int,
    mipmaps_resampling_type: PIL.Image.Resampling,
) -> PartialEncodeInfoDTO:
    image_encoder = ImageEncoder()
    encoded_palette_data: bytes = b""

    if entry_type == 1:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=16,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 2:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=256,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 3:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.RGBA5551,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 4:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.RGB888,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 5:
        encoded_image_data = rgba8888_data
    elif entry_type == 21:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.N64_BGR5A3,
            image_endianess="big",
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 22:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.ARGB8888,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 24:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            image_endianess="big",
            max_color_count=16,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 25:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            image_endianess="big",
            max_color_count=256,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 64:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=16,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 65:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=256,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 66:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.RGBT5551,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type in (88, 89):
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.RGB565,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 90:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.RGBX4444,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 91:
        encoded_image_data = rgba8888_data
    elif entry_type == 92:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=16,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 93:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=256,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 96:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC1_DXT1  # TODO - mipmaps
        )
    elif entry_type == 97:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC2_DXT3  # TODO - mipmaps
        )
    elif entry_type == 98:
        encoded_image_data = image_encoder.encode_compressed_image(
            rgba8888_data, img_width, img_height, ImageFormats.BC3_DXT5  # TODO - mipmaps
        )
    elif entry_type == 109:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.BGRA4444,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 120:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.BGR565,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 121:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=16,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 123:
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba8888_data,
            img_width,
            img_height,
            indexed_image_format,
            palette_format,
            max_color_count=256,
            number_of_mipmaps=mipmaps_count,
        )
    elif entry_type == 125:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.BGRA8888,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 126:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.BGRA5551,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    elif entry_type == 127:
        encoded_image_data = image_encoder.encode_image(
            rgba8888_data,
            img_width,
            img_height,
            ImageFormats.BGR888,
            number_of_mipmaps=mipmaps_count,
            mipmaps_resampling_type=mipmaps_resampling_type,
        )
    else:
        raise Exception(f"Image type {entry_type} not supported for encoding!")

    return PartialEncodeInfoDTO(encoded_image_data=encoded_image_data, encoded_palette_data=encoded_palette_data)
