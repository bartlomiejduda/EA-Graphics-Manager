"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from reversebox.common.logger import get_logger

from src.EA_Image.constants import IMPORT_IMAGES_SUPPORTED_TYPES

logger = get_logger(__name__)


def encode_ea_image(rgba_data: bytes, ea_dir) -> bytes:
    logger.info("Initializing encode_ea_image")
    entry_type: int = ea_dir.h_record_id

    if entry_type not in IMPORT_IMAGES_SUPPORTED_TYPES:
        raise Exception("Image type not supported for encoding!")

    if entry_type == 5:
        return rgba_data

    else:
        raise Exception("Image type not supported for encoding!")
