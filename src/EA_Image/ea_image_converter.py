"""
Copyright © 2023  Bartłomiej Duda
License: GPL-3.0 License
"""
import struct

from reversebox.io_files.bytes_handler import BytesHandler


class ImageDataConvertHandler:
    def __init__(self):
        pass

    # def convert_type_2_to_bmp(self, ea_dir_entry, ea_image):
    #     img_bpp = 8
    #     img_data = b""
    #     img_pal_data_size = len(ea_dir_entry.bin_attachments_list[0].raw_data)
    #     img_pal_data = b""
    #     img_height = ea_dir_entry.h_height
    #     img_width = ea_dir_entry.h_width
    #
    #     # skew fix
    #     read_count = 0
    #     skew_val = img_width % 4
    #     for _ in range(img_height):
    #         temp_row = b""
    #         for _ in range(img_width):
    #             pixel = struct.pack(
    #                 ea_image.f_endianess + "B", ea_dir_entry.raw_data[read_count]
    #             )
    #             read_count += 1
    #             temp_row += pixel
    #         if skew_val == 1:
    #             temp_row += b"\x00\x00"
    #         elif skew_val == 2:
    #             temp_row += b"x\00"
    #
    #         img_data += temp_row
    #
    #     # missing pixels fix
    #     img_size_calc = img_height * img_width
    #     diff = (
    #                    ea_dir_entry.h_size_of_the_block - ea_dir_entry.header_size
    #            ) - img_size_calc
    #     for _ in range(diff):
    #         pixel = b"\x00"
    #         img_data += pixel
    #
    #     # palette fix
    #     read_count = 0
    #     pal_range = int(img_pal_data_size / 4)
    #     for _ in range(pal_range):
    #         pal_entry1 = struct.pack(
    #             ea_image.f_endianess + "B",
    #             ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
    #         )
    #         read_count += 1
    #         pal_entry2 = struct.pack(
    #             ea_image.f_endianess + "B",
    #             ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
    #         )
    #         read_count += 1
    #         pal_entry3 = struct.pack(
    #             ea_image.f_endianess + "B",
    #             ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
    #         )
    #         read_count += 1
    #         pal_entry4 = struct.pack(
    #             ea_image.f_endianess + "B",
    #             ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
    #         )
    #         read_count += 1
    #         img_pal_data += (
    #                 pal_entry3 + pal_entry2 + pal_entry1 + pal_entry4
    #         )  # RGBA swap
    #
    #     bmp_object = BmpImg(
    #         img_width, img_height, img_bpp, img_data, img_pal_data
    #     )
    #     ea_dir_entry.img_convert_data = bmp_object.get_bmp_file_data()

    # TODO - move it to ReverseBox
    def convert_b8g8r8a8_to_r8b8g8a8(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 4
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            b_byte = bytes_handler.get_bytes(read_offset, 1)
            g_byte = bytes_handler.get_bytes(read_offset + 1, 1)
            r_byte = bytes_handler.get_bytes(read_offset + 2, 1)
            a_byte = bytes_handler.get_bytes(read_offset + 3, 1)
            single_pixel_data = r_byte + g_byte + b_byte + a_byte
            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # TODO - move it to ReverseBox
    def convert_r5g5b5p1_to_r8b8g8a8(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            input_pixel: bytes = bytes_handler.get_bytes(read_offset, 2)
            input_pixel_int = struct.unpack("<H", input_pixel)[0]

            def unpack_color(value, use_alpha=True):
                r = value & 0x1F
                g = value >> 5 & 0x1F
                b = value >> 10 & 0x1F
                a = value >> 15 & 0x1
                r = (r << 3) | (r >> 2)
                g = (g << 3) | (g >> 2)
                b = (b << 3) | (b >> 2)
                return (r << 24) | (g << 16) | (b << 8) | (0x00 if use_alpha and a == 0 else 0xFF)

            out_pixel_int = unpack_color(input_pixel_int, False)
            single_pixel_data = struct.pack(">I", out_pixel_int)

            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # TODO - move it to ReverseBox
    def convert_r8g8b8_to_r8b8g8a8(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 3
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            b_byte = bytes_handler.get_bytes(read_offset, 1)
            g_byte = bytes_handler.get_bytes(read_offset + 1, 1)
            r_byte = bytes_handler.get_bytes(read_offset + 2, 1)
            single_pixel_data = r_byte + g_byte + b_byte + b"\xFF"
            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # TODO - move it to ReverseBox
    def convert_r8g8b8a8pal_to_r8b8g8a8(self, image_data: bytes, palette_data: bytes) -> bytes:
        converted_raw_data = b""
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        bytes_per_pixel = 1
        bytes_per_palette_pixel = 4
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            palette_index = image_handler.get_bytes(read_offset, 1)
            palette_index_int = struct.unpack("B", palette_index)[0]
            read_offset += bytes_per_pixel

            palette_read_offset = palette_index_int * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            b_byte = palette_handler.get_bytes(palette_read_offset + 2, 1)
            a_byte = palette_handler.get_bytes(palette_read_offset + 3, 1)
            single_pixel_data = r_byte + g_byte + b_byte + a_byte
            converted_raw_data += single_pixel_data

        return converted_raw_data
