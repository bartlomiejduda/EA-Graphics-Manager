# -*- coding: utf-8 -*-

"""
Copyright © 2023  Bartłomiej Duda
License: GPL-3.0 License
"""

import os
import struct

from reversebox.common.logger import get_logger

from src.EA_Image.bin_attachment_entries import (
    CommentEntry,
    HotSpotEntry,
    ImgNameEntry,
    MetalBinEntry,
    PaletteEntry,
    UnknownEntry,
)
from src.EA_Image.data_read import get_utf8_string
from src.EA_Image.dir_entry import DirEntry
from src.EA_Image.ea_image_converter import ImageDataConvertHandler

logger = get_logger(__name__)


class EAImage:
    def __init__(self):
        self.sign = None
        self.total_f_size = -1
        self.num_of_entries = -1
        self.dir_id = None

        self.f_name = None
        self.f_path = None
        self.f_endianess = None
        self.f_endianess_desc = None
        self.f_size = None
        self.dir_entry_list = []
        self.ea_image_id = -1
        self.dir_entry_id = 0

        # fmt: off
        self.allowed_signatures = (
            "SHPI",  # PC games
            "SHPP",  # PS1 games
            "SHPS",  # PS2 games
            "SHPX",  # XBOX games
            "SHPM",  # PSP games
            "SHPG",  # WII games
        )
        # fmt: on

    def set_ea_image_id(self, in_ea_image_id):
        self.ea_image_id = in_ea_image_id

    def check_file_signature_and_size(self, in_file) -> tuple:
        try:
            # checking signature
            back_offset = in_file.tell()
            sign = get_utf8_string(in_file, 4)
            in_file.seek(back_offset)
            if sign not in self.allowed_signatures:
                error_msg = "File signature is not supported"
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

    def parse_header(self, in_file, in_file_path, in_file_name):
        self.sign = get_utf8_string(in_file, 4)

        self.f_path = in_file_path
        self.f_name = in_file_name
        self.f_size = os.path.getsize(self.f_path)
        back_offset = in_file.tell()

        # check endianess & file validity
        # fmt: off
        self.total_f_size = struct.unpack("<L", in_file.read(4))[0]
        if (self.total_f_size == self.f_size) or (self.total_f_size + 12 == self.f_size):  # fix for "CRCF" tail in some EA files
            self.f_endianess = "<"
            self.f_endianess_desc = "little"
        else:
            in_file.seek(back_offset)
            self.total_f_size = struct.unpack(">L", in_file.read(4))[0]
            if (self.total_f_size == self.f_size) or (self.total_f_size + 12 == self.f_size):  # fix for "CRCF" tail in some EA files
                self.f_endianess = ">"
                self.f_endianess_desc = "big"
            else:
                logger.warning("Warning! Can't get file endianess! File may be broken! Using little endian as default!")
                self.f_endianess = "<"
                self.f_endianess_desc = "little"

        self.num_of_entries = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]
        self.dir_id = in_file.read(4).decode("utf8")
        # fmt: on

    def parse_directory(self, in_file):
        # creating directory entries
        for i in range(self.num_of_entries):
            self.dir_entry_id += 1
            entry_id = str(self.ea_image_id) + "_direntry_" + str(self.dir_entry_id)
            entry_tag_bytes = in_file.read(4)
            entry_tag = entry_tag_bytes.decode("utf8")
            entry_offset = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]
            ea_dir_entry = DirEntry(entry_id, entry_tag, entry_offset)

            self.dir_entry_list.append(ea_dir_entry)  # dir entry is now initialized and can be added to the list

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

    def parse_dir_entry_header_and_data(self, in_file, ea_dir_entry):
        ea_dir_entry.set_entry_header(in_file, self.f_endianess)  # read entry header and set all values

        ea_dir_entry.set_raw_data(
            in_file,
            ea_dir_entry.start_offset + ea_dir_entry.header_size,
            ea_dir_entry.end_offset,
        )  # read raw entry data and set values

        ea_dir_entry.set_img_end_offset()  # this value is known only after reading data

    def parse_bin_attachments(self, in_file):
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

                # fix for entries with no attachments
                if in_file.tell() + ea_dir_entry.header_size >= ea_dir_entry.end_offset:
                    break  # no more binary attachments for this DIR entry

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
                    elif bin_att_rec_id in (33, 34, 35, 36, 41, 42, 45, 59):
                        bin_att_entry = PaletteEntry(bin_att_id, bin_att_start_offset)
                    else:
                        bin_att_entry = UnknownEntry(bin_att_id, bin_att_start_offset)
                        logger.warning(f"Unknown bin attachment entry ({str(hex(bin_att_rec_id))})!")

                    bin_att_entry.set_tag(bin_att_rec_id)
                    bin_att_entry.set_entry_header(in_file, self.f_endianess)
                    bin_att_entry.set_raw_data(in_file, in_file.tell(), ea_dir_entry.end_offset)

                    bin_att_entry.start_offset = bin_att_start_offset
                    bin_att_entry.end_offset = in_file.tell()

                    ea_dir_entry.bin_attachments_list.append(bin_att_entry)  # binary attachment is now parsed
                    # and can be added to the list

                    if bin_att_entry.end_offset >= ea_dir_entry.end_offset:
                        break  # no more binary attachments for this DIR entry

    def convert_images(self):
        conv_images_supported_types = [1, 2, 3, 4, 5, 65, 66, 125]

        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]
            entry_type = ea_dir_entry.h_record_id

            if entry_type not in conv_images_supported_types:
                logger.warning(
                    f'Warning! Image "{ea_dir_entry.tag}" with entry type {str(entry_type)} is not supported for image conversion! Skipping!'
                )
                continue

            logger.info(
                f'Starting conversion for image {str(i+1)}, img_type={str(entry_type)}, img_tag="{ea_dir_entry.tag}"...'
            )
            ea_dir_entry.is_img_convert_supported = True
            self.convert_image_data_for_export_and_preview(ea_dir_entry, entry_type)
            logger.info(
                f'Finished conversion for image {str(i + 1)}, img_type={str(entry_type)}, img_tag="{ea_dir_entry.tag}"...'
            )

    def convert_image_data_for_export_and_preview(self, ea_dir_entry, entry_type):
        logger.info(f'Initializing conversion function for img_type={str(entry_type)}, img_tag="{ea_dir_entry.tag}"...')

        def _get_palette_data_from_dir_entry(_ea_dir_entry) -> bytes:
            _palette_data: bytes = b""
            for attachment in _ea_dir_entry.bin_attachments_list:
                if isinstance(attachment, PaletteEntry):
                    _palette_data = attachment.raw_data
                    break
            return _palette_data

        if entry_type == 1:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_4bit_r8g8b8a8pal_to_r8b8g8a8(
                ea_dir_entry.raw_data, _get_palette_data_from_dir_entry(ea_dir_entry)
            )
        elif entry_type == 2:
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            if self.dir_id != "GIMX":  # temporary workaround for NHL 2001-2003 PS2 games
                palette_data = ImageDataConvertHandler().palette_ps2_unswizzle(palette_data)

            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_8bit_r8g8b8a8pal_to_r8b8g8a8(
                ea_dir_entry.raw_data, palette_data
            )
        elif entry_type == 3:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_r5g5b5p1_to_r8b8g8a8(
                ea_dir_entry.raw_data
            )
        elif entry_type == 4:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_r8g8b8_to_r8b8g8a8(ea_dir_entry.raw_data)
        elif entry_type == 5:
            ea_dir_entry.img_convert_data = ea_dir_entry.raw_data  # r8g8b8a8
        elif entry_type == 65:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_r5g5b5a1pal_to_r8b8g8a8(
                ea_dir_entry.raw_data, _get_palette_data_from_dir_entry(ea_dir_entry)
            )
        elif entry_type == 66:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_r5g5b5p1_to_r8b8g8a8(
                ea_dir_entry.raw_data
            )
        elif entry_type == 125:
            ea_dir_entry.img_convert_data = ImageDataConvertHandler().convert_b8g8r8a8_to_r8b8g8a8(
                ea_dir_entry.raw_data
            )
        else:
            logger.error(f"Unsupported type {entry_type} for convert and preview!")
            return
