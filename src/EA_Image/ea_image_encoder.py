"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from typing import Tuple

from reversebox.common.logger import get_logger
from reversebox.image.image_encoder import ImageEncoder
from reversebox.image.image_formats import ImageFormats

from src.EA_Image.constants import IMPORT_IMAGES_SUPPORTED_TYPES
from src.EA_Image.dir_entry import DirEntry

logger = get_logger(__name__)


def encode_ea_image(rgba_data: bytes, ea_dir: DirEntry) -> Tuple[bytes, bytes]:
    logger.info("Initializing encode_ea_image")
    entry_type: int = ea_dir.h_record_id
    encoded_palette_data: bytes = b""
    image_encoder = ImageEncoder()

    if entry_type not in IMPORT_IMAGES_SUPPORTED_TYPES:
        raise Exception("Image type not supported for encoding!")

    if entry_type == 1:  # TODO
        encoded_image_data, encoded_palette_data = image_encoder.encode_indexed_image(
            rgba_data, ea_dir.h_width, ea_dir.h_height, ImageFormats.PAL4, ImageFormats.RGBA8888
        )
    elif entry_type == 5:
        encoded_image_data = rgba_data

    else:
        raise Exception("Image type not supported for encoding!")

    return encoded_image_data, encoded_palette_data
