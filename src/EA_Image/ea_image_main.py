"""
Copyright © 2023-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import os
import struct
import traceback
from typing import Optional

from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.image_padding import psp_image_padding

from src.EA_Image.attachments.comment_entry import CommentEntry
from src.EA_Image.attachments.hot_spot_entry import HotSpotEntry
from src.EA_Image.attachments.img_name_entry import ImgNameEntry
from src.EA_Image.attachments.metal_bin_entry import MetalBinEntry
from src.EA_Image.attachments.palette_entry import PaletteEntry
from src.EA_Image.attachments.unknown_entry import UnknownEntry
from src.EA_Image.common_ea_dir import (
    get_palette_info_dto_from_dir_entry,
    handle_image_swizzle_logic,
    is_image_compressed,
    is_image_swizzled,
)
from src.EA_Image.constants import (
    CONVERT_IMAGES_SUPPORTED_TYPES,
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
    PALETTE_TYPES,
)
from src.EA_Image.data_read import get_null_terminated_string, get_string
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.dto import PaletteInfoDTO
from src.EA_Image.ea_image_decoder import decode_image_data_by_entry_type

logger = get_logger(__name__)


class EAImage:
    def __init__(self):
        self.sign = None
        self.total_f_size = -1
        self.total_f_data: Optional[bytes] = None
        self.is_total_f_data_compressed: bool = False
        self.num_of_entries = -1
        self.format_version = None
        self.header_and_toc_size = None  # new shape only

        self.f_name = None
        self.f_path = None
        self.f_endianess = None
        self.f_dir_endianess = None
        self.f_endianess_desc = None
        self.f_size = None
        self.dir_entry_list = []
        self.ea_image_id = -1
        self.dir_entry_id = 0

    def set_ea_image_id(self, in_ea_image_id):
        self.ea_image_id = in_ea_image_id

    def check_file_signature_and_size(self, in_file) -> tuple:
        try:
            # checking signature
            back_offset = in_file.tell()
            sign = get_string(in_file, 4)
            in_file.seek(back_offset)
            if len(sign) == 0:
                error_msg = "File is empty. No data to read!"
                logger.info(error_msg)
                return "FILE_IS_EMPTY", error_msg
            if sign not in OLD_SHAPE_ALLOWED_SIGNATURES and sign not in NEW_SHAPE_ALLOWED_SIGNATURES:
                error_msg = f'File signature "{sign}" is not supported'
                logger.info(error_msg)
                return "SIGN_NOT_SUPPORTED", error_msg

            # checking file size
            back_offset = in_file.tell()
            in_file.seek(0, os.SEEK_END)
            real_file_size = in_file.tell()
            in_file.seek(4)
            file_size_le = struct.unpack("<L", in_file.read(4))[0]
            in_file.seek(4)
            file_size_be = struct.unpack(">L", in_file.read(4))[0]
            in_file.seek(back_offset)
            # fmt: off
            if (file_size_le != real_file_size) and (file_size_be != real_file_size):

                # fix for "CRCF" tail in some EA files
                sign = b''
                try:
                    in_file.seek(real_file_size - 12)
                    sign = in_file.read(4)
                    in_file.seek(back_offset)
                except Exception as error:
                    logger.error(f"Can't check for CRCF signature! Error: {error}")

                if sign != b'CRCF':
                    error_msg = (
                        "Real file size doesn't match file total file size from header:\n"
                        + "Real_file_size: " + str(real_file_size) + "\n"
                        + "File_size_le: " + str(file_size_le) + "\n"
                        + "File_size_be: " + str(file_size_be)
                    )
                    logger.info(error_msg)
                    return "WRONG_SIZE_ERROR", error_msg
            # fmt: on
            return "OK", ""

        except Exception as error:
            error_msg = f"Can't read file signature or size! Error: {error}"
            logger.error(error_msg)
            return "CANT_READ_ERROR", error_msg

    def parse_header(self, in_file, in_file_path, in_file_name) -> bool:
        def _set_big_endianess():
            self.f_endianess = ">"
            self.f_endianess_desc = "big"

        def _set_little_endianess():
            self.f_endianess = "<"
            self.f_endianess_desc = "little"

        self.sign = get_string(in_file, 4)
        self.f_path = in_file_path
        self.f_name = in_file_name
        self.f_size = os.path.getsize(self.f_path)
        _set_little_endianess()
        self.total_f_size = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]

        if self.sign == "SHPG" or self.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            _set_big_endianess()
        else:
            _set_little_endianess()
        self.num_of_entries = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]
        if self.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.format_version = in_file.read(4).decode("utf8")  # e.g. "G354"
        elif self.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.header_and_toc_size = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]

        # set endianess for directory
        if self.sign in ("SHPG", "ShpF", "ShpS", "ShpX"):
            self.f_dir_endianess = ">"  # big
        else:
            self.f_dir_endianess = "<"  # little

        # set endianess for the rest of the file
        if self.sign in ("SHPG", "ShpG", "ShpM"):
            _set_big_endianess()
        else:
            _set_little_endianess()

        return True  # header has been parsed

    def parse_directory(self, in_file) -> bool:
        # creating directory entries
        for i in range(self.num_of_entries):
            self.dir_entry_id += 1
            entry_id = str(self.ea_image_id) + "_direntry_" + str(self.dir_entry_id)
            ea_dir_entry = None

            if self.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                entry_tag_bytes = in_file.read(4)
                entry_tag = entry_tag_bytes.decode("utf8")
                entry_offset = struct.unpack(self.f_dir_endianess + "L", in_file.read(4))[0]
                ea_dir_entry = DirEntry(entry_id, entry_tag, entry_offset)
            elif self.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                entry_offset = struct.unpack(self.f_dir_endianess + "L", in_file.read(4))[0]
                entry_size = struct.unpack(self.f_dir_endianess + "L", in_file.read(4))[0]  # noqa: F841
                entry_tag = get_null_terminated_string(in_file)
                ea_dir_entry = DirEntry(entry_id, entry_tag, entry_offset)

            self.dir_entry_list.append(ea_dir_entry)  # dir entry is now initialized and can be added to the list

        # sort dir entries by entry start offset
        # it can solve issues when dir entries are listed in random order in archive TOC
        # (e.g. The Need for Speed: Special Edition .FSH files)
        self.dir_entry_list.sort(key=lambda d_entry: d_entry.start_offset)

        # updating end offset for each entry
        # and parsing DIR entry data
        entry_num = 0
        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]
            entry_num += 1

            # set end offset for DIR entry
            if entry_num == self.num_of_entries:
                ea_dir_entry.end_offset = self.total_f_size
            else:
                ea_dir_entry.end_offset = self.dir_entry_list[i + 1].start_offset

            in_file.seek(ea_dir_entry.start_offset)
            self.parse_dir_entry_header_and_data(in_file, ea_dir_entry)

        return True  # directory has been parsed

    def parse_dir_entry_header_and_data(self, in_file, ea_dir_entry) -> bool:
        ea_dir_entry.set_entry_header(in_file, self.f_endianess, self.sign)  # read entry header and set all values

        ea_dir_entry.set_raw_data(
            in_file,
            ea_dir_entry.start_offset + ea_dir_entry.header_size,
            ea_dir_entry.end_offset,
        )  # read raw entry data and set values

        if self.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            ea_dir_entry.set_is_image_compressed_masked(in_file)
        ea_dir_entry.set_img_end_offset()  # this value is known only after reading data

        return True

    def parse_bin_attachments(self, in_file) -> bool:
        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]

            if (
                ea_dir_entry.if_next_entry_exist_flag is False
                and ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block == ea_dir_entry.end_offset
            ):
                pass  # no binary attachments for this DIR entry
            else:
                # there are some binary attachments (1 or more)
                bin_att_id_count = 0
                in_file.seek(
                    ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block
                )  # seek to offset of the first bin attachment

                # logic for entries with no attachments
                if in_file.tell() + ea_dir_entry.header_size >= ea_dir_entry.end_offset:
                    continue  # no more binary attachments for this DIR entry

                while 1:
                    bin_att_start_offset = in_file.tell()
                    bin_att_id_count += 1
                    bin_att_id = ea_dir_entry.id + "_binattach_" + str(bin_att_id_count)

                    bin_att_rec_id = struct.unpack(self.f_endianess + "B", in_file.read(1))[0]
                    in_file.seek(bin_att_start_offset)

                    if bin_att_rec_id == 105:
                        bin_att_entry = MetalBinEntry(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 111:
                        bin_att_entry = CommentEntry(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 112:
                        bin_att_entry = ImgNameEntry(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id == 124:
                        bin_att_entry = HotSpotEntry(bin_att_id, bin_att_start_offset)
                    elif bin_att_rec_id in PALETTE_TYPES:
                        bin_att_entry = PaletteEntry(bin_att_id, bin_att_start_offset)
                    else:
                        bin_att_entry = UnknownEntry(bin_att_id, bin_att_start_offset)
                        logger.warning(f"Unknown bin attachment entry ({str(hex(bin_att_rec_id))})!")

                    bin_att_entry.set_tag(bin_att_rec_id)
                    bin_att_entry.set_entry_header(in_file, self.f_endianess, self.sign)
                    bin_att_start_offset = in_file.tell()
                    bin_att_entry.set_raw_data(in_file, bin_att_start_offset, ea_dir_entry.end_offset)

                    bin_att_entry.start_offset = bin_att_start_offset
                    bin_att_entry.end_offset = in_file.tell()

                    ea_dir_entry.bin_attachments_list.append(bin_att_entry)  # binary attachment is now parsed
                    # and can be added to the list

                    if bin_att_entry.end_offset >= ea_dir_entry.end_offset:
                        break  # no more binary attachments for this DIR entry

        return True

    def convert_images(self, gui_main) -> bool:
        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]
            entry_type = ea_dir_entry.h_record_id

            if entry_type not in CONVERT_IMAGES_SUPPORTED_TYPES:
                logger.warning(
                    f'Warning! Image "{ea_dir_entry.tag}" with entry type {str(entry_type)} is not supported for image conversion! Skipping!'
                )
                continue

            logger.info(
                f'Starting conversion for image {str(i+1)}, img_type={str(entry_type)}, img_tag="{ea_dir_entry.tag}"...'
            )
            ea_dir_entry.is_img_convert_supported = True
            self.convert_image_data_for_export_and_preview(ea_dir_entry, entry_type, gui_main)
            logger.info(
                f'Finished conversion for image {str(i + 1)}, img_type={str(entry_type)}, img_tag="{ea_dir_entry.tag}"...'
            )
        return True

    def convert_image_data_for_export_and_preview(self, ea_dir_entry: DirEntry, entry_type: int, gui_main) -> bool:
        image_data: bytes = ea_dir_entry.raw_data

        # decompress logic
        if is_image_compressed(entry_type):
            image_data = RefpackHandler().decompress_data(image_data)

        entry_type = entry_type & 0x7F

        # unswizzling logic
        if is_image_swizzled(ea_dir_entry):
            image_data = handle_image_swizzle_logic(
                image_data, entry_type, ea_dir_entry.h_width, ea_dir_entry.h_height, self.sign, False
            )

        # padding logic
        if self.sign in ("SHPM", "ShpM"):  # PSP padding
            image_data = psp_image_padding(
                image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ea_dir_entry.h_image_bpp
            )

        # palette info logic
        palette_info_dto: PaletteInfoDTO = get_palette_info_dto_from_dir_entry(ea_dir_entry, self)

        # decoding logic
        try:
            ea_dir_entry.img_convert_data = decode_image_data_by_entry_type(
                entry_type, image_data, palette_info_dto, ea_dir_entry
            )
        except Exception as error:
            logger.error(f"Error while decoding EA image! Error: {error}")
            logger.error(traceback.format_exc())
            return False

        if not ea_dir_entry.img_convert_data:
            logger.error("Decoded image data is empty!")
            return False

        return True
