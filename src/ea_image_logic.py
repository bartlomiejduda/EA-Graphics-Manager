# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
"""


# Program tested on Python 3.7.0

import os
import struct
from src.logger import get_logger

logger = get_logger(__name__)


class BmpImg:
    class BmpHeader:
        def __init__(self, in_size, in_offset):
            self.bmp_magic = b"BM"
            self.bmp_size = in_size
            self.reserved = 0
            self.offset_im_data = in_offset

        def get_binary(self):
            return (
                struct.pack("2s", self.bmp_magic)
                + struct.pack("<L", self.bmp_size)
                + struct.pack("<L", self.reserved)
                + struct.pack("<L", self.offset_im_data)
            )

    class BmpInfoHeader:
        def __init__(self, in_width, in_height, in_bpp):
            self.info_header_size = 40
            self.num_of_planes = 1
            self.comp_type = 0
            self.comp_im_size = 0
            self.pref_hor_res = 0
            self.pref_vert_res = 0
            self.num_of_used_colors = 0
            self.num_of_imp_colors = 0

            self.im_width = in_width
            self.im_height = in_height
            self.bpp = in_bpp

        def get_binary(self):
            return (
                struct.pack("<L", self.info_header_size)
                + struct.pack("<L", self.im_width)
                + struct.pack("<L", self.im_height)
                + struct.pack("<H", self.num_of_planes)
                + struct.pack("<H", self.bpp)
                + struct.pack("<L", self.comp_type)
                + struct.pack("<L", self.comp_im_size)
                + struct.pack("<L", self.pref_hor_res)
                + struct.pack("<L", self.pref_vert_res)
                + struct.pack("<L", self.num_of_used_colors)
                + struct.pack("<L", self.num_of_imp_colors)
            )

    def __init__(self, in_width, in_height, in_bpp, in_image_data, in_palette_data):
        self.bmp_width = in_width
        self.bmp_height = in_height
        self.bmp_bpp = in_bpp
        self.bmp_data = in_image_data
        self.bmp_palette = in_palette_data

        self.data_size = len(self.bmp_data)
        self.palette_size = len(self.bmp_palette)
        self.bmp_size = 14 + 40 + self.palette_size + self.data_size
        self.data_offset = 14 + 40 + self.palette_size

        self.header = self.BmpHeader(self.data_size, self.data_offset)
        self.header_data = self.header.get_binary()

        self.info_header = self.BmpInfoHeader(
            self.bmp_width, self.bmp_height, self.bmp_bpp
        )
        self.info_header_data = self.info_header.get_binary()

    def get_bmp_file_data(self):
        return (
            self.header_data + self.info_header_data + self.bmp_palette + self.bmp_data
        )


class EAImage:
    class DirEntry:

        header_size = 16

        entry_types = {
            2: "2 | 0x02 | SKEWED IMAGE",
            33: "33 | 0x21 | PALETTE",
            34: "34 | 0x22 | PALETTE",
            35: "35 | 0x23 | PALETTE",
            36: "36 | 0x24 | PALETTE",
            41: "41 | 0x29 | PALETTE",
            42: "42 | 0x2A | PALETTE",
            45: "45 | 0x2D | PALETTE",
            64: "64 | 0x40 | 4-BIT IMG",
            65: "65 | 0x41 | 8-BIT IMG",
            66: "66 | 0x42 | 16-BIT IMG",
            96: "96 | 0x60 | DXT1",
            97: "97 | 0x61 | DXT3",
            98: "98 | 0x62 | DXT5",
            99: "99 | 0x63 | ETC1",
            100: "100 | 0x64 | PVRTC",
            102: "102 | 0x66 | 24-BIT IMG",
            104: "104 | 0x68 | 16-BIT IMG (484)",
            105: "105 | 0x69 | METAL BIN",
            106: "106 | 0x6A | 32-BIT IMG (1010102)",
            109: "109 | 0x6D | 16-BIT IMG (A4R4G4B4)",
            111: "111 | 0x6F | COMMENT",
            112: "112 | 0x70 | IMG NAME",
            120: "120 | 0x78 | 16-BIT IMG (A0R5G6B5)",
            121: "121 | 0x79 | IMG PAL-16",
            123: "123 | 0x7B | IMG PAL-256",
            124: "124 | 0x7C | HOT SPOT",
            125: "125 | 0x7D | 32-BIT IMG (A8R8G8B8)",
            126: "126 | 0x7E | 16-BIT IMG (A1R5G5B5)",
            127: "127 | 0x7F | 24-BIT IMG (A0R8G8B8)",
            131: "131 | 0x83 | 16-BIT IMG REFPACK",
        }

        def __init__(self, in_id, in_tag, in_offset):
            self.id = in_id
            self.tag = in_tag
            self.start_offset = in_offset
            self.end_offset = None
            self.raw_header = None
            self.raw_data_offset = None
            self.raw_data = None

            self.h_record_id = None
            self.h_size_of_the_block = None
            self.h_width = None
            self.h_height = None
            self.h_center_x = None
            self.h_center_y = None
            self.h_left_x_pos = None
            self.h_top_y_pos = None
            self.h_mipmaps_count = None

            self.bin_attachments_list = []
            self.if_next_entry_exist_flag = None
            self.is_img_convert_supported = False
            self.img_convert_type = None
            self.img_convert_data = None

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.h_width = self.get_uint16(in_file, endianess)
            self.h_height = self.get_uint16(in_file, endianess)
            self.h_center_x = self.get_uint16(in_file, endianess)
            self.h_center_y = self.get_uint16(in_file, endianess)
            self.h_left_x_pos, unk1 = self.get_uint12_uint4(in_file, endianess)
            self.h_top_y_pos, self.h_mipmaps_count = self.get_uint12_uint4(
                in_file, endianess
            )

        def set_raw_data(self, in_file, in_data_start_offset, in_data_end_offset=0):
            zero_size_flag = -1

            if self.h_size_of_the_block == 0:
                zero_size_flag = 1
                self.h_size_of_the_block = in_data_end_offset - in_data_start_offset

            self.raw_data_offset = in_data_start_offset
            in_file.seek(self.raw_data_offset)

            if zero_size_flag == 1:
                self.if_next_entry_exist_flag = False
                self.raw_data = in_file.read(self.h_size_of_the_block)
            else:
                self.if_next_entry_exist_flag = True
                self.raw_data = in_file.read(
                    self.h_size_of_the_block - self.header_size
                )

        def get_entry_type(self):
            result = self.entry_types.get(
                self.h_record_id, str(self.h_record_id) + " - UNKNOWN_TYPE"
            )
            return result

        @staticmethod
        def get_uint8(in_file, endianess):
            result = struct.unpack(endianess + "B", in_file.read(1))[0]
            return result

        @staticmethod
        def get_uint16(in_file, endianess):
            result = struct.unpack(endianess + "H", in_file.read(2))[0]
            return result

        @staticmethod
        def get_uint12_uint4(in_file, endianess):
            bytes2 = in_file.read(2)
            val_int = struct.unpack(endianess + "H", bytes2)[0]
            val_str = bin(val_int).lstrip("0b").zfill(16)

            uint4_str = val_str[0:4]
            uint4_int = int(uint4_str, 2)

            uint12_str = val_str[4:16]
            uint12_int = int(uint12_str, 2)

            out_list = [uint12_int, uint4_int]
            return out_list

        @staticmethod
        def get_uint24(in_file, endianess):
            if endianess == "<":
                result = struct.unpack(endianess + "I", in_file.read(3) + b"\x00")[0]
            else:
                result = struct.unpack(endianess + "I", b"\x00" + in_file.read(3))[0]
            return result

        @staticmethod
        def get_uint32(in_file, endianess):
            result = struct.unpack(endianess + "L", in_file.read(4))[0]
            return result

        @staticmethod
        def get_uint64(in_file, endianess):
            result = struct.unpack(endianess + "Q", in_file.read(8))[0]
            return result

    class BinAttachmentEntry(DirEntry):

        entry_tags = {
            33: "palette 0x21",
            34: "palette 0x22",
            35: "palette 0x23",
            36: "palette 0x24",
            41: "palette 0x29",
            42: "palette 0x2A",
            45: "palette 0x2D",
            105: "metal bin",
            111: "comment",
            112: "img name",
            124: "hot spot",
        }

        def __init__(self, in_id, in_offset):
            self.id = in_id
            self.tag = None
            self.start_offset = in_offset
            self.end_offset = None
            self.raw_header = None
            self.raw_data_offset = None
            self.raw_data = None

            self.h_record_id = None
            self.h_size_of_the_block = None

        def set_tag(self, in_entry_id):
            self.tag = self.entry_tags.get(
                in_entry_id, str(in_entry_id) + " - UNKNOWN_TYPE"
            )

    class MetalBinEntry(BinAttachmentEntry):
        header_size = 16

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.h_data_size = self.get_uint16(in_file, endianess)
            self.h_flags = self.get_uint16(in_file, endianess)
            self.h_unknown = self.get_uint64(in_file, endianess)

    class CommentEntry(BinAttachmentEntry):
        header_size = 8

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.h_comment_length = self.get_uint32(in_file, endianess)

    class ImgNameEntry(BinAttachmentEntry):
        header_size = 4

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)

    class HotSpotEntry(BinAttachmentEntry):
        header_size = 8

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.num_of_pairs = self.get_uint32(in_file, endianess)

    class PaletteEntry(BinAttachmentEntry):
        header_size = 16

        def set_header(self, in_file, endianess):
            self.h_record_id = self.get_uint8(in_file, endianess)
            self.h_size_of_the_block = self.get_uint24(in_file, endianess)
            self.pal_width = self.get_uint16(in_file, endianess)
            self.pal_height = self.get_uint16(in_file, endianess)
            self.pal_entries = self.get_uint16(in_file, endianess)
            self.unk1 = self.get_uint16(in_file, endianess)
            self.unk2 = self.get_uint16(in_file, endianess)
            self.unk3 = self.get_uint16(in_file, endianess)

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

        self.allowed_signatures = (
            "SHPI",  # PC games
            "SHPP",  # PS1 games
            "SHPS",  # PS2 games
            "ShpX",
            "SHPX",  # XBOX games
            "SHPM",  # PSP games
        )

    def set_ea_image_id(self, in_ea_image_id):
        self.ea_image_id = in_ea_image_id

    def check_file_signature(self, in_file):
        try:
            sign = in_file.read(4).decode("utf8")
            in_file.seek(0)
            if sign not in self.allowed_signatures:
                raise
            return 0
        except:
            return -1

    def parse_header(self, in_file, in_file_path, in_file_name):
        self.sign = in_file.read(4).decode("utf8")

        self.f_path = in_file_path
        self.f_name = in_file_name
        self.f_size = os.path.getsize(self.f_path)
        back_offset = in_file.tell()

        # check endianess & file validity
        self.total_f_size = struct.unpack("<L", in_file.read(4))[0]
        if self.total_f_size == self.f_size:
            self.f_endianess = "<"
            self.f_endianess_desc = "little"
        else:
            in_file.seek(back_offset)
            self.total_f_size = struct.unpack(">L", in_file.read(4))[0]
            if self.total_f_size == self.f_size:
                self.f_endianess = ">"
                self.f_endianess_desc = "big"
            else:
                logger.warning(
                    "Warning! Can't get file endianess! File may be broken! Using little endian as default!"
                )
                self.f_endianess = "<"
                self.f_endianess_desc = "little"

        self.num_of_entries = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]
        self.dir_id = in_file.read(4).decode("utf8")

    def parse_directory(self, in_file):

        # creating directory entries
        for i in range(self.num_of_entries):
            self.dir_entry_id += 1
            entry_id = str(self.ea_image_id) + "_direntry_" + str(self.dir_entry_id)
            entry_tag = in_file.read(4).decode("utf8")
            entry_offset = struct.unpack(self.f_endianess + "L", in_file.read(4))[0]
            ea_dir_entry = self.DirEntry(entry_id, entry_tag, entry_offset)

            self.dir_entry_list.append(
                ea_dir_entry
            )  # dir entry is now initialized and can be added to the list

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
        ea_dir_entry.set_header(
            in_file, self.f_endianess
        )  # read entry header and set all values

        ea_dir_entry.set_raw_data(
            in_file,
            ea_dir_entry.start_offset + ea_dir_entry.header_size,
            ea_dir_entry.end_offset,
        )  # read raw entry data and set values

    def parse_bin_attachments(self, in_file):

        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]

            if (
                ea_dir_entry.if_next_entry_exist_flag is False
                and ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block
                == ea_dir_entry.end_offset
            ):
                pass  # no binary attachments for this DIR entry
            else:

                # there are some binary attachments (1 or more)
                bin_att_id_count = 0
                in_file.seek(
                    ea_dir_entry.start_offset + ea_dir_entry.h_size_of_the_block
                )  # seek to offset of the first bin attachment

                while 1:
                    bin_att_start_offset = in_file.tell()
                    bin_att_id_count += 1
                    bin_att_id = ea_dir_entry.id + "_binattach_" + str(bin_att_id_count)

                    bin_att_rec_id = struct.unpack(
                        self.f_endianess + "B", in_file.read(1)
                    )[0]
                    in_file.seek(bin_att_start_offset)

                    if bin_att_rec_id == 105:
                        bin_att_entry = self.MetalBinEntry(
                            bin_att_id, bin_att_start_offset
                        )
                    elif bin_att_rec_id == 111:
                        bin_att_entry = self.CommentEntry(
                            bin_att_id, bin_att_start_offset
                        )
                    elif bin_att_rec_id == 112:
                        bin_att_entry = self.ImgNameEntry(
                            bin_att_id, bin_att_start_offset
                        )
                    elif bin_att_rec_id == 124:
                        bin_att_entry = self.HotSpotEntry(
                            bin_att_id, bin_att_start_offset
                        )
                    elif bin_att_rec_id in (33, 34, 35, 36, 41, 42, 45):
                        bin_att_entry = self.PaletteEntry(
                            bin_att_id, bin_att_start_offset
                        )
                    else:
                        logger.error(
                            "Unknown bin attachment entry ("
                            + str(hex(bin_att_rec_id))
                            + ")! Aborting!"
                        )
                        break

                    bin_att_entry.set_tag(bin_att_rec_id)
                    back_offset = in_file.tell()
                    bin_att_entry.set_header(in_file, self.f_endianess)
                    bin_att_entry.set_raw_data(
                        in_file, in_file.tell(), ea_dir_entry.end_offset
                    )

                    bin_att_entry.start_offset = bin_att_start_offset
                    bin_att_entry.end_offset = in_file.tell()

                    ea_dir_entry.bin_attachments_list.append(
                        bin_att_entry
                    )  # binary attachment is now parsed
                    # and can be added to the list

                    if bin_att_entry.end_offset >= ea_dir_entry.end_offset:
                        break  # no more binary attachments for this DIR entry

    def convert_images(self):

        conv_images_supported_types = [2]

        for i in range(self.num_of_entries):
            ea_dir_entry = self.dir_entry_list[i]

            entry_type = ea_dir_entry.h_record_id

            if entry_type not in conv_images_supported_types:
                logger.warning(
                    "Warning! Entry type "
                    + str(entry_type)
                    + " is not supported"
                    + " for image conversion! Skipping!"
                )
                continue

            else:
                logger.info(
                    "Converting image type "
                    + str(entry_type)
                    + ", number "
                    + str(i + 1)
                    + "..."
                )
                ea_dir_entry.is_img_convert_supported = True

            if entry_type == 2:
                self.img_convert_type = "BMP"

                img_bpp = 8
                img_data = b""
                img_pal_data_size = len(ea_dir_entry.bin_attachments_list[0].raw_data)
                img_pal_data = b""
                img_height = ea_dir_entry.h_height
                img_width = ea_dir_entry.h_width

                # skew fix
                read_count = 0
                skew_val = img_width % 4
                for i in range(img_height):
                    temp_row = b""
                    for j in range(img_width):
                        pixel = struct.pack(
                            self.f_endianess + "B", ea_dir_entry.raw_data[read_count]
                        )
                        read_count += 1
                        temp_row += pixel
                    if skew_val == 1:
                        temp_row += b"\x00\x00"
                    elif skew_val == 2:
                        temp_row += b"x\00"

                    img_data += temp_row

                # missing pixels fix
                img_size_calc = img_height * img_width
                diff = (
                    ea_dir_entry.h_size_of_the_block - ea_dir_entry.header_size
                ) - img_size_calc
                for i in range(diff):
                    pixel = b"\x00"
                    img_data += pixel

                # palette fix
                read_count = 0
                pal_range = int(img_pal_data_size / 4)
                for i in range(pal_range):
                    pal_entry1 = struct.pack(
                        self.f_endianess + "B",
                        ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
                    )
                    read_count += 1
                    pal_entry2 = struct.pack(
                        self.f_endianess + "B",
                        ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
                    )
                    read_count += 1
                    pal_entry3 = struct.pack(
                        self.f_endianess + "B",
                        ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
                    )
                    read_count += 1
                    pal_entry4 = struct.pack(
                        self.f_endianess + "B",
                        ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
                    )
                    read_count += 1
                    img_pal_data += (
                        pal_entry3 + pal_entry2 + pal_entry1 + pal_entry4
                    )  # RGBA swap

                bmp_object = BmpImg(
                    img_width, img_height, img_bpp, img_data, img_pal_data
                )
                ea_dir_entry.img_convert_data = bmp_object.get_bmp_file_data()
