# -*- coding: utf-8 -*-

"""
Copyright © 2023-2024  Bartłomiej Duda
License: GPL-3.0 License
"""

import os
import struct
import traceback

from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.image_decoder import ImageDecoder
from reversebox.image.image_formats import ImageFormats
from reversebox.image.palettes.palette_random import generate_random_palette
from reversebox.image.swizzling.swizzle_gamecube import unswizzle_gamecube
from reversebox.image.swizzling.swizzle_morton import unswizzle_morton
from reversebox.image.swizzling.swizzle_ps2 import (
    unswizzle_ps2,
    unswizzle_ps2_ea_4bit,
    unswizzle_ps2_palette,
)
from reversebox.image.swizzling.swizzle_psp import unswizzle_psp

from src.EA_Image.bin_attachment_entries import (
    CommentEntry,
    HotSpotEntry,
    ImgNameEntry,
    MetalBinEntry,
    PaletteEntry,
    UnknownEntry,
)
from src.EA_Image.common import get_bpp_for_image_type
from src.EA_Image.constants import (
    CONVERT_IMAGES_SUPPORTED_TYPES,
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
    PALETTE_TYPES,
)
from src.EA_Image.data_read import get_null_terminated_string, get_string
from src.EA_Image.dir_entry import DirEntry

logger = get_logger(__name__)


class EAImage:
    def __init__(self):
        self.sign = None
        self.total_f_size = -1
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

    def convert_image_data_for_export_and_preview(self, ea_dir_entry, entry_type, gui_main) -> bool:
        def _get_palette_data_and_id_from_dir_entry(_ea_dir_entry) -> tuple:
            # try to get palette from binary attachment first
            _palette_data: bytes = b""
            _entry_id: int = 33  # default palette
            _h_default_x_position = -1
            for attachment in _ea_dir_entry.bin_attachments_list:
                if isinstance(attachment, PaletteEntry):
                    _palette_data = attachment.raw_data
                    _entry_id = attachment.h_record_id
                    _h_default_x_position = attachment.h_default_x_position
                    break

            if _palette_data and len(_palette_data) > 0:
                if _entry_id in (33, 59) and _h_default_x_position & 0x2000:  # check for palette swizzle flag
                    return _entry_id, unswizzle_ps2_palette(_palette_data)

                return _entry_id, _palette_data  # return palette from binary attachment

            # try to get palette from other dir entry
            for i in range(self.num_of_entries):
                ea_dir_entry = self.dir_entry_list[i]
                if ea_dir_entry.h_record_id in PALETTE_TYPES:
                    if (
                        ea_dir_entry.h_record_id in (33, 59) and ea_dir_entry.h_default_x_position & 0x2000
                    ):  # check for palette swizzle flag
                        return ea_dir_entry.h_record_id, unswizzle_ps2_palette(ea_dir_entry.raw_data)

                    return ea_dir_entry.h_record_id, ea_dir_entry.raw_data  # return palette from other dir entry

            logger.warn("Warning! Couldn't find palette data!")
            return _entry_id, generate_random_palette()  # return random palette if no palette has been found

        def _get_indexed_image_format(palette_entry_id: int, bpp: int, palette_size: int) -> ImageFormats:
            if bpp == 4:
                if palette_entry_id == 33:
                    return ImageFormats.PAL4_RGBA8888
                elif palette_entry_id == 34:
                    return ImageFormats.PAL4_RGBX6666  # TODO
                elif palette_entry_id == 35:
                    return ImageFormats.PAL4_XBGR1555
                elif palette_entry_id == 36:
                    return ImageFormats.PAL4_RGB888
                elif palette_entry_id == 41:
                    return ImageFormats.PAL4_RGB565
                elif palette_entry_id == 42:  # TODO - check RGB/BGR logic
                    return ImageFormats.PAL4_BGRA8888 if palette_size == 1024 else ImageFormats.PAL4_BGR888
                elif palette_entry_id == 45:
                    return ImageFormats.PAL4_XRGB1555  # TODO - check if format is ok
                elif palette_entry_id == 50:
                    return ImageFormats.PAL4_RGB5A3
                elif palette_entry_id == 58:
                    return ImageFormats.PAL4_RGBA8888  # TODO - check if format is ok
                elif palette_entry_id == 59:
                    return ImageFormats.PAL4_RGBA8888
                else:
                    logger.warning(f"Palette ID={palette_entry_id} not supported for bpp=4!")

            elif bpp == 8:
                if palette_entry_id == 33:
                    return ImageFormats.PAL8_RGBA8888
                elif palette_entry_id == 34:
                    return ImageFormats.PAL8_RGBX6666
                elif palette_entry_id == 35:
                    return ImageFormats.PAL8_XBGR1555
                elif palette_entry_id == 36:
                    return ImageFormats.PAL8_RGB888
                elif palette_entry_id == 41:
                    return ImageFormats.PAL8_RGB565
                elif palette_entry_id == 42:  # TODO - check RGB/BGR logic
                    return ImageFormats.PAL8_BGRA8888 if palette_size == 1024 else ImageFormats.PAL8_BGR888
                elif palette_entry_id == 45:
                    return ImageFormats.PAL8_XRGB1555  # TODO - check if format is ok
                elif palette_entry_id == 50:
                    return ImageFormats.PAL8_RGB5A3
                elif palette_entry_id == 58:
                    return ImageFormats.PAL8_RGBA8888  # TODO - check if format is ok
                elif palette_entry_id == 59:
                    return ImageFormats.PAL8_RGBA8888
                else:
                    logger.warning(f"Palette ID={palette_entry_id} not supported for bpp=8!")

            else:
                logger.warning(f"Bpp {bpp} not supported for indexed images!")

            logger.warning(f"Image format has not been found for palette_id={palette_entry_id} and bpp={bpp}")
            return ImageFormats.PAL4_RGB565  # default

        def _is_image_swizzled() -> bool:
            if ea_dir_entry.h_flag2_swizzled or ea_dir_entry.new_shape_flag_swizzled:
                return True
            return False

        ea_image_decoder = ImageDecoder()
        image_data: bytes = ea_dir_entry.raw_data
        is_image_compressed: int = entry_type & 0x80  # 0 - not compressed / 128 - compressed
        entry_type = entry_type & 0x7F
        if is_image_compressed == 128:
            image_data = RefpackHandler().decompress_data(image_data)

        # unswizzling logic
        if _is_image_swizzled():
            try:
                if entry_type >= 8 and entry_type <= 15:  # for PS2 games (GST textures)
                    pass  # swizzling handled by GST decoder
                elif entry_type == 30:  # for WII games (DXT1/CMPR textures)
                    pass  # swizzling handled by N64 decoder
                elif self.sign in ("SHPX", "ShpX", "SHPI", "ShpF"):  # for XBOX and PC games
                    image_data = unswizzle_morton(
                        image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, get_bpp_for_image_type(entry_type)
                    )
                elif self.sign in ("SHPM", "ShpM"):  # for PSP games
                    image_data = unswizzle_psp(
                        image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, get_bpp_for_image_type(entry_type)
                    )
                elif self.sign in ("SHPS", "ShpS") and (
                    entry_type < 8 or entry_type > 15
                ):  # for PS2 games (standard textures)
                    bpp = get_bpp_for_image_type(entry_type)
                    if bpp == 4:
                        image_data = unswizzle_ps2_ea_4bit(image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, bpp)
                    elif bpp in (8, 15, 16):
                        image_data = unswizzle_ps2(image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, bpp)
                    else:
                        logger.warning(f"PS2 unswizzle for bpp {bpp} is not supported yet!")
                elif self.sign in ("SHPG", "ShpG"):  # for WII/GameCube games
                    image_data = unswizzle_gamecube(
                        image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, get_bpp_for_image_type(entry_type)
                    )
                else:
                    logger.warning(f"Swizzling for signature {self.sign} is not supported yet!")
            except Exception as error:
                logger.error(f"Error while unswizzling images! Error: {error}")
                logger.error(traceback.format_exc())

        # decoding logic
        try:
            if entry_type == 1:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 2:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)

                if len(palette_data) == 0:
                    logger.error("Error while converting palette data for type 2!")
                    return False

                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 3:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ABGR1555
                )
            elif entry_type == 4:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
                )
            elif entry_type == 5:
                ea_dir_entry.img_convert_data = image_data  # r8g8b8a8
            elif entry_type == 8:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST121,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 9:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST221,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 10:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST421,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 11:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST821,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 12:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST122,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 13:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST222,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 14:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST422,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 15:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_gst_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.GST822,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    is_swizzled=_is_image_swizzled(),
                )
            elif entry_type == 20:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565, image_endianess="big"
                )
            elif entry_type == 22:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB8888
                )
            elif entry_type == 24:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    palette_endianess="big",
                )
            elif entry_type == 25:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                    palette_endianess="big",
                )
            elif entry_type == 30:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_n64_image(
                    image_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.N64_CMPR,
                )
            elif entry_type == 33:
                ea_dir_entry.img_convert_data = image_data  # palette
            elif entry_type == 34:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
                )  # palette
            elif entry_type == 35:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
                )  # palette
            elif entry_type == 36:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
                )  # palette
            elif entry_type == 42:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGBA8888
                )  # palette
            elif entry_type == 59:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
                )  # palette
            elif entry_type == 64:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 65:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 66:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XBGR1555
                )
            elif entry_type == 67:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB888
                )
            elif entry_type == 88:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
                )
            elif entry_type == 89:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
                )
            elif entry_type == 90:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGRX4444
                )
            elif entry_type == 91:
                ea_dir_entry.img_convert_data = image_data  # r8g8b8a8
            elif entry_type == 92:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 93:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 96:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_compressed_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.DXT1
                )
            elif entry_type == 97:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_compressed_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.DXT3
                )
            elif entry_type == 98:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_compressed_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.DXT5
                )
            elif entry_type == 100:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.N64_I8
                )
            elif entry_type == 101:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_n64_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.N64_IA8
                )
            elif entry_type == 104:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_yuv_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.YUV422_YUY2
                )
            elif entry_type == 109:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.ARGB4444
                )
            elif entry_type == 115:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data[1024:],
                    image_data[:1024],
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.PAL8_RGBA8888,
                )
            elif entry_type == 119:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data[64:],
                    image_data[:64],
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    ImageFormats.PAL4_RGBA8888,
                )
            elif entry_type == 120:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.RGB565
                )
            elif entry_type == 121:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 123:
                palette_id, palette_data = _get_palette_data_and_id_from_dir_entry(ea_dir_entry)
                # for i in range(1024):
                #     palette_data += b"\x00"  # workaround for Need For Speed 2 PC, e.g. "TR000_QFS.fsh"
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_indexed_image(
                    image_data,
                    palette_data,
                    ea_dir_entry.h_width,
                    ea_dir_entry.h_height,
                    _get_indexed_image_format(palette_id, get_bpp_for_image_type(entry_type), len(palette_data)),
                )
            elif entry_type == 125:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGRA8888
                )
            elif entry_type == 126:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.XRGB1555
                )
            elif entry_type == 127:
                ea_dir_entry.img_convert_data = ea_image_decoder.decode_image(
                    image_data, ea_dir_entry.h_width, ea_dir_entry.h_height, ImageFormats.BGR888
                )
            else:
                logger.error(f"Unsupported type {entry_type} for convert and preview!")
                return False
        except Exception as error:
            logger.error(f"Error while decoding EA image! Error: {error}")
            logger.error(traceback.format_exc())
            return False

        return True
