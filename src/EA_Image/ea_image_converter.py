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

    # TODO - temp
    def get_int_from_bits(self, n: int, start_bit: int, number_of_bits: int) -> int:
        n = n >> (31 - start_bit - number_of_bits)
        mask = ~(-1 << number_of_bits)
        result = n & mask
        return result

    # TODO - temp
    def get_int_from_bits2(self, n: int, start_bit: int, number_of_bits: int) -> int:
        bit_string = "0b"
        for i in range(number_of_bits):
            bit_string += "1"
        bit_value = int(bit_string, 2)

        return (n << start_bit) & bit_value

    # TODO - temp
    def get_int_from_bits3(self, n: int, start_bit: int, number_of_bits: int) -> int:
        mask = ((1 << number_of_bits) - 1) << start_bit
        isolatedXbits = n & mask
        return isolatedXbits

    # TODO - move it to ReverseBox
    def convert_r5g5b5p1_to_r8b8g8a8(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            input_pixel: bytes = bytes_handler.get_bytes(read_offset, 2)
            input_pixel_int = struct.unpack(">H", input_pixel)[0]
            # print("AA: " + str(bin(input_pixel_int)))

            # r_byte_value = (input_pixel_int & 0b1111100000000000)
            # g_byte_value = (input_pixel_int & 0b0000011111000000)
            # b_byte_value = (input_pixel_int & 0b0000000000011111)

            # byte1 = struct.unpack("B", bytes_handler.get_bytes(read_offset, 1))[0]
            # byte2 = struct.unpack("B", bytes_handler.get_bytes(read_offset + 1, 1))[0]
            r_byte_value = (input_pixel_int << 4) & 0b111111
            g_byte_value = (input_pixel_int >> 5) & 0x3F
            b_byte_value = input_pixel_int & 11
            #
            # # r_byte_value = self.get_int_from_bits3(input_pixel_int, 1, 5)
            # # g_byte_value = self.get_int_from_bits3(input_pixel_int, 5, 6)
            # # b_byte_value = self.get_int_from_bits3(input_pixel_int, 6, 5)
            #
            r_byte = struct.pack(">B", r_byte_value)
            g_byte = struct.pack(">B", g_byte_value)
            b_byte = struct.pack(">B", b_byte_value)
            a_byte = struct.pack(">B", 255)
            single_pixel_data = r_byte + g_byte + b_byte + a_byte

            # def unpackColor(value, useAlpha=True):
            #     # r = (value & 0b11111)
            #     # g = (value >> 5 & 0b11111)
            #     # b = (value >> 10 & 0b11111)
            #     # a = (value >> 15 & 0b1)
            #     a = (value & 0b1)
            #     b = (value >> 1 & 0b11111)
            #     g = (value >> 6 & 0b11111)
            #     r = (value >> 11 & 0b11111)
            #     r = r << 3 | (r >> 2)
            #     g = g << 3 | (g >> 2)
            #     b = b << 3 | (b >> 2)
            #     return ((r << 24) | (g << 16) | (b << 8) | (0x00 if useAlpha and a == 0 else 0xFF))
            #
            # single_pixel_data = struct.pack(">I", unpackColor(input_pixel_int, False))

            # VH = struct.unpack("B", bytes_handler.get_bytes(read_offset, 1))[0]
            # VL = struct.unpack("B", bytes_handler.get_bytes(read_offset+1, 1))[0]
            #
            # b5 = VH & 0b11111
            # g6 = ((VH & 0b11100000) >> 5 | (VL & 0b11) << 3) & 0b111111
            # r5 = (VL >> 3) & 0b11111
            # r_byte = byte(b5)
            # g_byte = struct.pack(">B", g6)
            # b_byte = struct.pack(">B", r5)
            # a_byte = struct.pack(">B", 255)
            # single_pixel_data = r_byte + g_byte + b_byte + a_byte

            # https://github.com/Sudomemo/sudomemo-utils/blob/master/python/ugoImage.py
            # https://github.com/humbertokramm/RGB565toRGB888toPNG_-python-/blob/master/teste.py

            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data
