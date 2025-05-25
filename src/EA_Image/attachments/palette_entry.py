from src.EA_Image.attachments.bin_attachment_entry import BinAttachmentEntry
from src.EA_Image.constants import (
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
)
from src.EA_Image.data_read import get_uint8, get_uint16, get_uint24, get_uint32


class PaletteEntry(BinAttachmentEntry):
    header_size = 0

    def __init__(self, in_id, in_offset):
        super().__init__(in_id, in_offset)
        self.new_shape_palette_offset = None
        self.new_shape_palette_data_size = None
        self.new_shape_reserved1 = None
        self.new_shape_reserved2 = None
        self.h_default_x_position = -1
        self.h_default_y_position = -1

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
