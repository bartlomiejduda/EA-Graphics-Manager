from reversebox.common.common import convert_int_to_hex_string

from src.EA_Image.common import get_bpp_for_image_type
from src.EA_Image.constants import (
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
)
from src.EA_Image.data_read import (
    get_new_shape_uint24_flags,
    get_uint8,
    get_uint12_and_flags,
    get_uint12_uint4,
    get_uint16,
    get_uint24,
    get_uint32,
)


class DirEntry:
    header_size: int = 0

    entry_types = {
        1: "1 | 0x01 | PAL4",
        2: "2 | 0x02 | PAL8",
        3: "3 | 0x03 | RGBA5551",
        4: "4 | 0x04 | RGB888",
        5: "5 | 0x05 | RGBA8888",
        8: "8 | 0x08 | GST 121",
        9: "9 | 0x09 | GST 221",
        10: "10 | 0x0A | GST 421",
        11: "11 | 0x0B | GST 821",
        12: "12 | 0x0C | GST 122",
        13: "13 | 0x0D | GST 222",
        14: "14 | 0x0E | GST 422",
        15: "15 | 0x0F | GST 822",
        20: "20 | 0x14 | RGB565",
        22: "22 | 0x16 | ABGR8888",
        24: "24 | 0x18 | PAL4",
        25: "25 | 0x19 | PAL8",
        30: "30 | 0x1E | DXT1/CMPR",
        33: "33 | 0x21 | PALETTE 32-BIT 8888",
        34: "34 | 0x22 | PALETTE 24-BIT 666",
        35: "35 | 0x23 | PALETTE",
        36: "36 | 0x24 | PALETTE 24-BIT 888",
        41: "41 | 0x29 | PALETTE 16-BIT 565",
        42: "42 | 0x2A | PALETTE 32-BIT 8888",
        44: "44 | 0x2C | PALETTE 32-BIT 8565",
        45: "45 | 0x2D | PALETTE 15-BIT 555",
        46: "46 | 0x2E | PALETTE 32-BIT 8555",
        47: "47 | 0x2F | PALETTE 24-BIT 888",
        48: "48 | 0x30 | PALETTE 16-BIT IA8",
        49: "49 | 0x31 | PALETTE 16-BIT 565",
        50: "50 | 0x32 | PALETTE 16-BIT 3555",
        58: "58 | 0x3A | PALETTE",
        59: "59 | 0x3B | PALETTE",
        64: "64 | 0x40 | PAL4",
        65: "65 | 0x41 | PAL8",
        66: "66 | 0x42 | R5G5B5P1",
        67: "67 | 0x43 | RGB888",
        88: "88 | 0x58 | RGB565",
        89: "89 | 0x59 | RGB565",
        90: "90 | 0x5A | RGBA4444",
        91: "91 | 0x5B | RGBA8888",
        92: "92 | 0x5C | PAL4",
        93: "93 | 0x5D | PAL8",
        96: "96 | 0x60 | DXT1",
        97: "97 | 0x61 | DXT3",
        98: "98 | 0x62 | DXT5",
        99: "99 | 0x63 | ETC1",
        100: "100 | 0x64 | A8",
        101: "101 | 0x65 | IA8",
        102: "102 | 0x66 | 24-BIT IMG",
        104: "104 | 0x68 | YUY2 (484)",
        105: "105 | 0x69 | METAL BIN",
        106: "106 | 0x6A | 32-BIT IMG (1010102)",
        108: "108 | 0x6C | YUV (YUI)",
        109: "109 | 0x6D | ARGB4444",
        111: "111 | 0x6F | COMMENT",
        112: "112 | 0x70 | IMG NAME",
        115: "115 | 0x73 | PAL8",
        119: "119 | 0x77 | PAL4",
        120: "120 | 0x78 | RGB565",
        121: "121 | 0x79 | PAL4",
        123: "123 | 0x7B | PAL8",
        124: "124 | 0x7C | HOT SPOT",
        125: "125 | 0x7D | ARGB8888",
        126: "126 | 0x7E | XRGB1555",
        127: "127 | 0x7F | BGR888",
        130: "130 | 0x82 | PAL8",
        131: "131 | 0x83 | XBGR1555",
        192: "192 | 0xC0 | PAL4",
        193: "193 | 0xC1 | PAL8",
        194: "194 | 0xC2 | XBGR1555",
        237: "237 | 0xED | ARGB4444",
        248: "248 | 0xF8 | RGB565",
        251: "251 | 0xFB | PAL8",
    }

    def __init__(self, in_id, in_tag, in_offset):
        self.id = in_id
        self.tag = in_tag
        self.start_offset = in_offset
        self.end_offset = None
        self.raw_header = None
        self.raw_data_offset = None
        self.raw_data_size = None
        self.raw_data = None

        self.h_record_id = None
        self.h_record_id_masked = None
        self.h_is_image_compressed_masked = None
        self.h_size_of_the_block = None
        self.h_width = None
        self.h_height = None
        self.h_center_x = None
        self.h_center_y = None
        self.h_default_x_position = None
        self.h_flag1_referenced = None
        self.h_flag2_swizzled = None
        self.h_flag3_transposed = None
        self.h_flag4_reserved = None
        self.h_default_y_position = None
        self.h_mipmaps_count = None
        self.h_entry_header_offset = None
        self.h_entry_end_offset = None
        self.h_file_data_first_2_bytes = None
        self.h_image_bpp = None

        self.bin_attachments_list = []
        self.if_next_entry_exist_flag = None
        self.is_img_convert_supported = False
        self.img_convert_data = None

        # new shape fields
        self.new_shape_flags = None
        self.new_shape_flags_hex_str = None
        self.new_shape_flag_new_format = None
        self.new_shape_flag_compressed = None
        self.new_shape_flag_swizzled = None
        self.new_shape_number_of_mipmaps = None

    def set_entry_header(self, in_file, endianess: str, ea_image_sign: str) -> bool:
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.header_size = 16
            self.h_entry_header_offset = in_file.tell()
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_record_id_masked = self.h_record_id & 0x7F
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.h_width = get_uint16(in_file, endianess)
            self.h_height = get_uint16(in_file, endianess)
            self.h_center_x = get_uint16(in_file, endianess)
            self.h_center_y = get_uint16(in_file, endianess)
            (
                self.h_default_x_position,
                self.h_flag1_referenced,
                self.h_flag2_swizzled,
                self.h_flag3_transposed,
                self.h_flag4_reserved,
            ) = get_uint12_and_flags(in_file, endianess)
            self.h_default_y_position, self.h_mipmaps_count = get_uint12_uint4(in_file, endianess)
            self.h_image_bpp = get_bpp_for_image_type(self.h_record_id_masked)
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.header_size = 32
            self.h_entry_header_offset = in_file.tell()
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.new_shape_flags_hex_str = convert_int_to_hex_string(self.new_shape_flags)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.raw_data_offset = self.h_entry_header_offset + get_uint32(in_file, endianess)
            self.raw_data_size = get_uint32(in_file, endianess)
            self.h_default_x_position = get_uint32(in_file, endianess)
            self.h_default_y_position = get_uint32(in_file, endianess)
            self.h_width = get_uint32(in_file, endianess)
            self.h_height = get_uint32(in_file, endianess)
            self.h_image_bpp = get_bpp_for_image_type(self.h_record_id)
            (
                self.new_shape_flag_new_format,
                self.new_shape_flag_compressed,
                self.new_shape_flag_swizzled,
                self.new_shape_number_of_mipmaps,
            ) = get_new_shape_uint24_flags(self.new_shape_flags)

        return True  # image header has been parsed

    def set_raw_data(self, in_file, in_data_start_offset, in_data_end_offset=0) -> bool:
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
            self.raw_data = in_file.read(self.h_size_of_the_block - self.header_size)

        self.raw_data_size = len(self.raw_data)
        return True

    def set_img_end_offset(self) -> bool:
        self.h_entry_end_offset = self.raw_data_offset + self.raw_data_size
        return True

    def set_is_image_compressed_masked(self, in_file) -> bool:
        current_offset = in_file.tell()
        in_file.seek(self.raw_data_offset)
        self.h_file_data_first_2_bytes = in_file.read(2)
        in_file.seek(current_offset)

        is_image_compressed_masked: int = self.h_record_id & 0x80  # 0 - not compressed / 128 - compressed

        def _get_img_compressed_string(img_compressed_flag: int, first_2_bytes: bytes) -> str:
            if img_compressed_flag == 128 and first_2_bytes == b"\x10\xFB":
                return "REFPACK"
            elif img_compressed_flag == 128 and first_2_bytes in (b"\x18\xFB", b"\x1A\xFB", b"\x20\xFB"):
                return "DXT"
            elif img_compressed_flag == 128 and first_2_bytes == b"MG":
                return "MPEG"
            elif img_compressed_flag == 0:
                return "NONE"
            else:
                return "UNKNOWN"

        self.h_is_image_compressed_masked = _get_img_compressed_string(
            is_image_compressed_masked, self.h_file_data_first_2_bytes
        )
        return True

    def get_entry_type(self) -> str:
        result: str = self.entry_types.get(
            self.h_record_id,
            str(self.h_record_id) + " | " + "0x%02X" % int(self.h_record_id) + " | UNKNOWN_TYPE",
        )
        return result
