from src.EA_Image.attachments.bin_attachment_entry import BinAttachmentEntry
from src.EA_Image.constants import (
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
)
from src.EA_Image.data_read import get_uint8, get_uint24, get_uint32


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
