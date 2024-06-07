"""
Copyright © 2024  Bartłomiej Duda
License: GPL-3.0 License
"""

# fmt: off


def get_bpp_for_image_type(ea_img_type: int) -> int:
    if ea_img_type == 0x44:
        return 1
    elif ea_img_type in (0x01, 0x10, 0x18, 0x1E, 0x40, 0x5C, 0x60, 0x63, 0x79, 0x7A):
        return 4
    elif ea_img_type in (0x02, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x11, 0x12, 0x19, 0x41, 0x5D, 0x61, 0x62, 0x64, 0x7B):
        return 8
    elif ea_img_type in (0x1C, 0x6C):
        return 12
    elif ea_img_type in (0x03, 0x15, 0x20, 0x32, 0x39, 0x59, 0x7E):
        return 15
    elif ea_img_type in (0x13, 0x14, 0x1A, 0x23, 0x27, 0x28, 0x29, 0x2D, 0x30, 0x31, 0x38, 0x3A, 0x42, 0x58, 0x5A, 0x65, 0x67, 0x68, 0x6D, 0x78):
        return 16
    elif ea_img_type in (0x04, 0x22, 0x24, 0x43, 0x66, 0x7F):
        return 24
    elif ea_img_type in (0x05, 0x16, 0x21, 0x2A, 0x2C, 0x2E, 0x3B, 0x5B, 0x6A, 0x7D):
        return 32
    else:
        raise Exception(f"Image type {str(ea_img_type)} not supported! Can't get bpp info!")
