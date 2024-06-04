"""
Copyright © 2024  Bartłomiej Duda
License: GPL-3.0 License
"""


def get_bpp_for_image_type(ea_img_type: int) -> int:
    if ea_img_type == 0x23:
        return 16
    elif ea_img_type == 0x40:
        return 4
    elif ea_img_type == 0x41:
        return 8
    elif ea_img_type == 0x42:
        return 16
    elif ea_img_type == 0x43:
        return 24
    elif ea_img_type == 0x44:
        return 1
    elif ea_img_type == 0x30:
        return 16
    elif ea_img_type == 0x31:
        return 16
    elif ea_img_type == 0x32:
        return 15
    elif ea_img_type == 0x10:
        return 4
    elif ea_img_type == 0x11:
        return 8
    elif ea_img_type == 0x12:
        return 8
    elif ea_img_type == 0x13:
        return 16
    elif ea_img_type == 0x14:
        return 16
    elif ea_img_type == 0x15:
        return 15
    elif ea_img_type == 0x16:
        return 32
    elif ea_img_type == 0x18:
        return 4
    elif ea_img_type == 0x19:
        return 8
    elif ea_img_type == 0x1A:
        return 16
    elif ea_img_type == 0x1E:
        return 4
    elif ea_img_type == 0x1C:
        return 12
    elif ea_img_type == 0x38:
        return 16
    elif ea_img_type == 0x39:
        return 15
    elif ea_img_type == 0x3A:
        return 16
    elif ea_img_type == 0x3B:
        return 32
    elif ea_img_type == 0x58:
        return 16
    elif ea_img_type == 0x59:
        return 15
    elif ea_img_type == 0x5A:
        return 16
    elif ea_img_type == 0x5B:
        return 32
    elif ea_img_type == 0x5C:
        return 4
    elif ea_img_type == 0x5D:
        return 8
    elif ea_img_type == 0x20:
        return 15
    elif ea_img_type == 0x21:
        return 32
    elif ea_img_type == 0x01:
        return 4
    elif ea_img_type == 0x02:
        return 8
    elif ea_img_type == 0x03:
        return 15
    elif ea_img_type == 0x04:
        return 24
    elif ea_img_type == 0x05:
        return 32
    elif ea_img_type == 0x08:
        return 8
    elif ea_img_type == 0x09:
        return 8
    elif ea_img_type == 0x0A:
        return 8
    elif ea_img_type == 0x0B:
        return 8
    elif ea_img_type == 0x0C:
        return 8
    elif ea_img_type == 0x0D:
        return 8
    elif ea_img_type == 0x0E:
        return 8
    elif ea_img_type == 0x0F:
        return 8
    elif ea_img_type == 0x22:
        return 24
    elif ea_img_type == 0x24:
        return 24
    elif ea_img_type == 0x29:
        return 16
    elif ea_img_type == 0x2A:
        return 32
    elif ea_img_type == 0x2C:
        return 32
    elif ea_img_type == 0x2D:
        return 16
    elif ea_img_type == 0x2E:
        return 32
    elif ea_img_type == 0x60:
        return 4
    elif ea_img_type == 0x61:
        return 8
    elif ea_img_type == 0x62:
        return 8
    elif ea_img_type == 0x64:
        return 8
    elif ea_img_type == 0x68:
        return 16
    elif ea_img_type == 0x6C:
        return 12
    elif ea_img_type == 0x6D:
        return 16
    elif ea_img_type == 0x79:
        return 4
    elif ea_img_type == 0x7A:
        return 4
    elif ea_img_type == 0x7B:
        return 8
    elif ea_img_type == 0x7D:
        return 32
    elif ea_img_type == 0x78:
        return 16
    elif ea_img_type == 0x67:
        return 16
    elif ea_img_type == 0x7E:
        return 15
    elif ea_img_type == 0x7F:
        return 24
    elif ea_img_type == 0x65:
        return 16
    elif ea_img_type == 0x66:
        return 24
    elif ea_img_type == 0x6A:
        return 32
    elif ea_img_type == 0x27:
        return 16
    elif ea_img_type == 0x28:
        return 16
    elif ea_img_type == 0x63:
        return 4
    else:
        raise Exception(f"Not supported bpp for image type {str(ea_img_type)}!")
