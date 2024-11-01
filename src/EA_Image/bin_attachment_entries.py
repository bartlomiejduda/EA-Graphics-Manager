from src.EA_Image.constants import (
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
)
from src.EA_Image.data_read import (
    get_uint8,
    get_uint16,
    get_uint24,
    get_uint32,
    get_uint64,
)
from src.EA_Image.dir_entry import DirEntry


class BinAttachmentEntry(DirEntry):
    entry_tags = {
        33: "palette 0x21",
        34: "palette 0x22",
        35: "palette 0x23",
        36: "palette 0x24",
        41: "palette 0x29",
        42: "palette 0x2A",
        45: "palette 0x2D",
        50: "palette 0x32",
        58: "palette 0x3A",
        59: "palette 0x3B",
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
            in_entry_id,
            str(in_entry_id) + " | " + "0x%02X" % int(in_entry_id) + " | UNKNOWN_BIN_TYPE",
        )


class MetalBinEntry(BinAttachmentEntry):
    header_size = 8
    new_shape_data_offset = None
    new_shape_data_size = None

    def __init__(self, in_id, in_offset):
        super().__init__(in_id, in_offset)
        self.h_unknown = None
        self.h_flags = None
        self.h_data_size = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.h_data_size = get_uint16(in_file, endianess)
            self.h_flags = get_uint16(in_file, endianess)
            self.h_unknown = get_uint64(in_file, endianess)
            self.header_size = 16
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_data_offset = get_uint32(in_file, endianess)
            self.new_shape_data_size = get_uint32(in_file, endianess)
            self.header_size = 16


class CommentEntry(BinAttachmentEntry):
    header_size = 8
    new_shape_data_offset = None
    new_shape_data_size = None

    def __init__(self, in_id, in_offset):
        super().__init__(in_id, in_offset)
        self.h_comment_length = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.h_comment_length = get_uint32(in_file, endianess)
            self.header_size = 8
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_data_offset = get_uint32(in_file, endianess)
            self.new_shape_data_size = get_uint32(in_file, endianess)
            self.header_size = 16


class ImgNameEntry(BinAttachmentEntry):
    header_size = 0
    new_shape_data_offset = None
    new_shape_data_size = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.header_size = 4
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_data_offset = get_uint32(in_file, endianess)
            self.new_shape_data_size = get_uint32(in_file, endianess)
            self.header_size = 16


class UnknownEntry(BinAttachmentEntry):
    header_size = 0
    new_shape_data_offset = None
    new_shape_data_size = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.header_size = 4
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_data_offset = get_uint32(in_file, endianess)
            self.new_shape_data_size = get_uint32(in_file, endianess)
            self.header_size = 16


class HotSpotEntry(BinAttachmentEntry):
    header_size = 0

    def __init__(self, in_id, in_offset):
        super().__init__(in_id, in_offset)
        self.num_of_pairs = None
        self.new_shape_data_offset = None
        self.new_shape_data_size = None
        self.new_shape_center_x = None
        self.new_shape_center_y = None
        self.new_shape_dimension = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.num_of_pairs = get_uint32(in_file, endianess)
            self.header_size = 8
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_data_offset = get_uint32(in_file, endianess)
            self.new_shape_data_size = get_uint32(in_file, endianess)
            self.new_shape_center_x = get_uint32(in_file, endianess)
            self.new_shape_center_y = get_uint32(in_file, endianess)
            self.new_shape_dimension = get_uint32(in_file, endianess)
            self.num_of_pairs = get_uint32(in_file, endianess)
            self.header_size = 32


class PaletteEntry(BinAttachmentEntry):
    header_size = 0

    def __init__(self, in_id, in_offset):
        super().__init__(in_id, in_offset)
        self.new_shape_palette_offset = None
        self.new_shape_palette_data_size = None
        self.new_shape_reserved1 = None
        self.new_shape_reserved2 = None

    def set_entry_header(self, in_file, endianess, ea_image_sign: str):
        if ea_image_sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.h_size_of_the_block = get_uint24(in_file, endianess)
            self.h_width = get_uint16(in_file, endianess)
            self.h_height = get_uint16(in_file, endianess)
            self.h_center_x = get_uint16(in_file, endianess)
            self.h_center_y = get_uint16(in_file, endianess)
            self.h_default_x_position = get_uint16(in_file, endianess)  # shape X
            self.h_default_y_position = get_uint16(in_file, endianess)  # shape Y
            self.header_size = 16
        elif ea_image_sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.h_record_id = get_uint8(in_file, endianess)
            self.new_shape_flags = get_uint24(in_file, endianess)
            self.h_size_of_the_block = get_uint32(in_file, endianess)
            self.new_shape_palette_offset = get_uint32(in_file, endianess)
            self.new_shape_palette_data_size = get_uint32(in_file, endianess)
            self.new_shape_reserved1 = get_uint32(in_file, endianess)
            self.new_shape_reserved2 = get_uint32(in_file, endianess)
            self.h_width = get_uint32(in_file, endianess)
            self.h_height = get_uint32(in_file, endianess)
            self.header_size = 32
