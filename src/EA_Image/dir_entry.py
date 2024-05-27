from src.EA_Image.data_read import (
    get_uint8,
    get_uint12_and_flags,
    get_uint12_uint4,
    get_uint16,
    get_uint24,
)


class DirEntry:
    header_size = 16

    entry_types = {
        1: "1 | 0x01 | PAL4_RGBA8888",
        2: "2 | 0x02 | PAL8_RGBA8888",
        3: "3 | 0x03 | RGBA5551",
        4: "4 | 0x04 | RGB888",
        5: "5 | 0x05 | RGBA8888",
        14: "14 | 0x0E | 8-BIT IMG + SWIZ",
        33: "33 | 0x21 | PALETTE",
        34: "34 | 0x22 | PALETTE",
        35: "35 | 0x23 | PALETTE",
        36: "36 | 0x24 | PALETTE",
        41: "41 | 0x29 | PALETTE",
        42: "42 | 0x2A | PALETTE",
        45: "45 | 0x2D | PALETTE",
        58: "58 | 0x3A | PALETTE",
        59: "59 | 0x3B | PALETTE",
        64: "64 | 0x40 | PAL4_RGBX5551",
        65: "65 | 0x41 | PAL8_RGBX5551",
        66: "66 | 0x42 | R5G5B5P1",
        67: "67 | 0x43 | RGB888",
        88: "88 | 0x58 | RGB565",
        89: "89 | 0x59 | RGB565",
        90: "90 | 0x5A | RGBA4444",
        91: "91 | 0x5B | RGBA8888",
        92: "92 | 0x5C | PAL4_RGBA8888",
        93: "93 | 0x5D | PAL8_RGBA8888",
        96: "96 | 0x60 | DXT1",
        97: "97 | 0x61 | DXT3",
        98: "98 | 0x62 | DXT5",
        99: "99 | 0x63 | ETC1",
        100: "100 | 0x64 | PVRTC",
        102: "102 | 0x66 | 24-BIT IMG",
        104: "104 | 0x68 | 16-BIT IMG (484)",
        105: "105 | 0x69 | METAL BIN",
        106: "106 | 0x6A | 32-BIT IMG (1010102)",
        109: "109 | 0x6D | ARGB4444",
        111: "111 | 0x6F | COMMENT",
        112: "112 | 0x70 | IMG NAME",
        115: "115 | 0x73 | PAL8_RGBA8888",
        119: "119 | 0x77 | PAL4_RGBA8888",
        120: "120 | 0x78 | RGB565",
        121: "121 | 0x79 | PAL4_RGB888",
        123: "123 | 0x7B | PAL8_RGB888",
        124: "124 | 0x7C | HOT SPOT",
        125: "125 | 0x7D | ARGB8888",
        126: "126 | 0x7E | XRGB1555",
        127: "127 | 0x7F | BGR888",
        130: "130 | 0x82 | PAL8_RGBA8888",
        131: "131 | 0x83 | XBGR1555",
        192: "192 | 0xC0 | PAL4_RGBX5551",
        193: "193 | 0xC1 | PAL8_RGBX5551",
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

        self.bin_attachments_list = []
        self.if_next_entry_exist_flag = None
        self.is_img_convert_supported = False
        self.img_convert_data = None

    def set_entry_header(self, in_file, endianess):
        self.h_entry_header_offset = in_file.tell()
        self.h_record_id = get_uint8(in_file, endianess)
        self.h_record_id_masked = self.h_record_id & 0x7F
        is_image_compressed_masked: int = self.h_record_id & 0x80  # 0 - not compressed / 128 - refpack compressed

        def _get_img_compressed_string(img_compressed_flag: int) -> str:
            if img_compressed_flag == 128:
                return "REFPACK"
            elif img_compressed_flag == 0:
                return "NONE"
            else:
                return "UNKNOWN"

        self.h_is_image_compressed_masked = _get_img_compressed_string(is_image_compressed_masked)
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
            self.raw_data = in_file.read(self.h_size_of_the_block - self.header_size)

        self.raw_data_size = len(self.raw_data)

    def set_img_end_offset(self):
        self.h_entry_end_offset = self.raw_data_offset + self.raw_data_size

    def get_entry_type(self):
        result = self.entry_types.get(
            self.h_record_id,
            str(self.h_record_id) + " | " + "0x%02X" % int(self.h_record_id) + " | UNKNOWN_TYPE",
        )
        return result
