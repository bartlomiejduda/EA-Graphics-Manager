# -*- coding: utf-8 -*-

"""
Copyright © 2023  Bartłomiej Duda
License: GPL-3.0 License
"""

import os
import struct

from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.image_decoder import ImageDecoder
from reversebox.image.image_formats import ImageFormats
from reversebox.image.palettes.palette_random import generate_random_palette
from reversebox.image.swizzling.swizzle_ps2 import unswizzle_ps2_palette
from reversebox.image.swizzling.swizzle_psp import unswizzle_psp

from src.EA_Image.bin_attachment_entries import (
    CommentEntry,
    HotSpotEntry,
    ImgNameEntry,
    MetalBinEntry,
    PaletteEntry,
    UnknownEntry,
)
from src.EA_Image.constants import CONVERT_IMAGES_SUPPORTED_TYPES, PALETTE_TYPES
from src.EA_Image.data_read import get_utf8_string
from src.EA_Image.dir_entry import DirEntry

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
            "SHPG",  # WII/Gamecube games
            "SHPA",  # Game Boy Advance games
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
            if len(sign) == 0:
                error_msg = "File is empty. No data to read!"
                logger.info(error_msg)
                return "FILE_IS_EMPTY", error_msg
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

        ea_dir_entry.set_is_image_compressed_masked(in_file)
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
                    elif bin_att_rec_id in PALETTE_TYPES:
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

    def convert_images(self, gui_main):
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

    def convert_image_data_for_export_and_preview(self, ea_dir_entry, entry_type, gui_main):
        def _get_palette_data_from_dir_entry(_ea_dir_entry) -> bytes:
            # try to get palette from binary attachment first
            _palette_data: bytes = b""
            for attachment in _ea_dir_entry.bin_attachments_list:
                if isinstance(attachment, PaletteEntry):
                    _palette_data = attachment.raw_data
                    break

            if _palette_data and len(_palette_data) > 0:
                return _palette_data  # return palette from binary attachment

            # try to get palette from other dir entry
            for i in range(self.num_of_entries):
                ea_dir_entry = self.dir_entry_list[i]
                if ea_dir_entry.h_record_id in PALETTE_TYPES:
                    return ea_dir_entry.raw_data  # return palette from other dir entry

            logger.warn("Warning! Couldn't find palette data!")
            return generate_random_palette()  # return random palette if no palette has been found

        ea_image_decoder = ImageDecoder()

        if entry_type == 1:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                _get_palette_data_from_dir_entry(ea_dir_entry),
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL4_RGBA8888,
            )
        elif entry_type == 2:
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            if gui_main.enable_swizzling_type2_menu_option.get():
                palette_data = unswizzle_ps2_palette(palette_data)

            if len(palette_data) == 0:
                logger.error("Error while converting palette data for type 2!")
                return

            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                palette_data,
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL8_RGBA8888,
            )
        elif entry_type == 3:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ABGR1555
            )
        elif entry_type == 4:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
            )
        elif entry_type == 5:
            ea_dir_entry.img_convert_data = ea_dir_entry.raw_data  # r8g8b8a8
        elif entry_type == 14:
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            palette_data = unswizzle_ps2_palette(palette_data)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                ea_dir_entry.raw_data,
                palette_data,
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.GST422,
                is_swizzled=True,
            )
        elif entry_type == 33:
            ea_dir_entry.img_convert_data = ea_dir_entry.raw_data  # palette
        elif entry_type == 34:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
            )  # palette
        elif entry_type == 35:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
            )  # palette
        elif entry_type == 59:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
            )  # palette
        elif entry_type == 64:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                _get_palette_data_from_dir_entry(ea_dir_entry),
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL4_RGBX5551,
            )
        elif entry_type == 65:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                _get_palette_data_from_dir_entry(ea_dir_entry),
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL8_RGBX5551,
            )
        elif entry_type == 66:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XBGR1555
            )
        elif entry_type == 67:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
            )
        elif entry_type == 88:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
            )
        elif entry_type == 89:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
            )
        elif entry_type == 90:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBA4444
            )
        elif entry_type == 91:
            if ea_dir_entry.h_flag2_swizzled:
                unswizzled_image_data: bytes = unswizzle_psp(
                    ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, 32
                )
                ea_dir_entry.img_convert_data = unswizzled_image_data
            else:
                ea_dir_entry.img_convert_data = ea_dir_entry.raw_data  # r8g8b8a8
        elif entry_type == 92:
            unswizzled_image_data: bytes = unswizzle_psp(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, 4
            )
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                unswizzled_image_data,
                _get_palette_data_from_dir_entry(ea_dir_entry),
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL4_RGBA8888,
            )
        elif entry_type == 93:
            unswizzled_image_data: bytes = unswizzle_psp(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, 8
            )
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                unswizzled_image_data,
                _get_palette_data_from_dir_entry(ea_dir_entry),
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL8_RGBA8888,
            )
        elif entry_type == 96:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_compressed_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.DXT1
            )
        elif entry_type == 97:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_compressed_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.DXT3
            )
        elif entry_type == 109:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB4444
            )
        elif entry_type == 115:
            image_data = ea_dir_entry.raw_data[1024:]
            palette_data = ea_dir_entry.raw_data[:1024]
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                image_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.PAL8_RGBA8888
            )
        elif entry_type == 119:
            image_data = ea_dir_entry.raw_data[64:]
            palette_data = ea_dir_entry.raw_data[:64]
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                image_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.PAL4_RGBA8888
            )
        elif entry_type == 120:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
            )
        elif entry_type == 121:
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                palette_data,
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL4_RGB888,
            )
        elif entry_type == 123:
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                ea_dir_entry.raw_data,
                palette_data,
                ea_dir_entry.h_width,
                ea_dir_entry.h_height,
                ImageFormats.PAL8_RGB888,
            )
        elif entry_type == 125:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB8888
            )
        elif entry_type == 126:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
            )
        elif entry_type == 127:
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                ea_dir_entry.raw_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGR888
            )
        elif entry_type == 130:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                decompressed_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.PAL8_RGBA8888
            )
        elif entry_type == 131:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                decompressed_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XBGR1555
            )
        elif entry_type == 192:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                decompressed_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.PAL4_RGBX5551
            )
        elif entry_type == 193:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                decompressed_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.PAL8_RGBX5551
            )
        elif entry_type == 194:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                decompressed_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XBGR1555
            )
        elif entry_type == 237:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                decompressed_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB4444
            )
        elif entry_type == 248:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                decompressed_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
            )
        elif entry_type == 251:
            decompressed_data: bytes = RefpackHandler().decompress_data(ea_dir_entry.raw_data)
            palette_data = _get_palette_data_from_dir_entry(ea_dir_entry)
            if len(palette_data) < 1024:
                img_format = ImageFormats.PAL8_RGB888
            else:
                img_format = ImageFormats.PAL8_RGBA8888
            ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                decompressed_data, palette_data, ea_dir_entry.h_width, ea_dir_entry.h_height, img_format
            )
        else:
            logger.error(f"Unsupported type {entry_type} for convert and preview!")
            return

        return
