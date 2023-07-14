import struct


# TODO - move it to ReverseBox
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


# TODO - move it to ReverseBox
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


# TODO - move it to ReverseBox
class BmpImg:
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

        self.header = BmpHeader(self.data_size, self.data_offset)
        self.header_data = self.header.get_binary()

        self.info_header = BmpInfoHeader(self.bmp_width, self.bmp_height, self.bmp_bpp)
        self.info_header_data = self.info_header.get_binary()

    def get_bmp_file_data(self):
        return self.header_data + self.info_header_data + self.bmp_palette + self.bmp_data
