from src.EA_Image.data_read import get_uint8, get_uint12_uint4, get_uint16, get_uint24


class DirEntry:
    header_size = 16

    entry_types = {
        2: "2 | 0x02 | 8-BIT IMG, 256 PAL",
        33: "33 | 0x21 | PALETTE",
        34: "34 | 0x22 | PALETTE",
        35: "35 | 0x23 | PALETTE",
        36: "36 | 0x24 | PALETTE",
        41: "41 | 0x29 | PALETTE",
        42: "42 | 0x2A | PALETTE",
        45: "45 | 0x2D | PALETTE",
        59: "59 | 0x3B | PALETTE",
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
        self.raw_data_size = None
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
        self.h_entry_header_offset = None
        self.h_entry_end_offset = None

        self.bin_attachments_list = []
        self.if_next_entry_exist_flag = None
        self.is_img_convert_supported = False
        self.img_convert_type = None
        self.img_convert_data = None

    def set_entry_header(self, in_file, endianess):
        self.h_entry_header_offset = in_file.tell()
        self.h_record_id = get_uint8(in_file, endianess)
        self.h_size_of_the_block = get_uint24(in_file, endianess)
        self.h_width = get_uint16(in_file, endianess)
        self.h_height = get_uint16(in_file, endianess)
        self.h_center_x = get_uint16(in_file, endianess)
        self.h_center_y = get_uint16(in_file, endianess)
        self.h_left_x_pos, _ = get_uint12_uint4(in_file, endianess)
        self.h_top_y_pos, self.h_mipmaps_count = get_uint12_uint4(in_file, endianess)

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
            str(self.h_record_id)
            + " | "
            + "0x%02X" % int(self.h_record_id)
            + " | UNKNOWN_TYPE",
        )
        return result
