"""
Copyright © 2023  Bartłomiej Duda
License: GPL-3.0 License
"""
import struct

from PIL import Image
from reversebox.common.logger import get_logger
from reversebox.io_files.bytes_handler import BytesHandler

logger = get_logger(__name__)


# TODO - move it to ReverseBox
class EAImageDecoder:
    def __init__(self):
        pass

    def _unpack_2bytes_color_rgbp5551(self, value, use_alpha=True):
        r = value & 0x1F
        g = value >> 5 & 0x1F
        b = value >> 10 & 0x1F
        a = value >> 15 & 0x1
        r = (r << 3) | (r >> 2)
        g = (g << 3) | (g >> 2)
        b = (b << 3) | (b >> 2)
        return (r << 24) | (g << 16) | (b << 8) | (0x00 if use_alpha and a == 0 else 0xFF)

    def _unpack_2bytes_color_argb5551(self, value, use_alpha=True):
        r = value & 0x1F
        g = value >> 5 & 0x1F
        b = value >> 10 & 0x1F
        a = value >> 15 & 0x1
        r = (r << 3) | (r >> 2)
        g = (g << 3) | (g >> 2)
        b = (b << 3) | (b >> 2)
        return (b << 24) | (g << 16) | (r << 8) | (0x00 if use_alpha and a == 0 else 0xFF)

    def _unpack_2bytes_color_rgba4444(self, byte1, byte2):
        r = (byte1 >> 4) * 16
        a = (byte1 & 15) * 16
        b = (byte2 >> 4) * 16
        g = (byte2 & 15) * 16
        return (r << 16) | (g << 8) | b | (a << 24)

    # EA Image type 125
    def convert_bgra8888_to_rgba8888(self, image_data: bytes) -> bytes:
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

    # EA Image type 3, 35, 59, 66, 88, 89
    def convert_rgbp5551_to_rgba8888(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            input_pixel: bytes = bytes_handler.get_bytes(read_offset, 2)
            input_pixel_int = struct.unpack("<H", input_pixel)[0]

            out_pixel_int = self._unpack_2bytes_color_rgbp5551(input_pixel_int, False)
            single_pixel_data = struct.pack(">I", out_pixel_int)

            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # EA Image type 126
    def convert_argb5551_to_rgba8888(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            input_pixel: bytes = bytes_handler.get_bytes(read_offset, 2)
            input_pixel_int = struct.unpack("<H", input_pixel)[0]

            out_pixel_int = self._unpack_2bytes_color_argb5551(input_pixel_int, False)
            single_pixel_data = struct.pack(">I", out_pixel_int)

            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # EA Image type 90
    def convert_rgba4444_to_rgba8888(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            input_value_1: bytes = bytes_handler.get_bytes(read_offset, 1)
            input_value_1_int = struct.unpack("B", input_value_1)[0]
            input_value_2: bytes = bytes_handler.get_bytes(read_offset + 1, 1)
            input_value_2_int = struct.unpack("B", input_value_2)[0]

            out_pixel_int = self._unpack_2bytes_color_rgba4444(input_value_1_int, input_value_2_int)
            single_pixel_data = struct.pack(">I", out_pixel_int)

            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # EA Image type 4, 67
    def convert_rgb888_to_rgba8888(self, image_data: bytes) -> bytes:
        converted_raw_data = b""
        bytes_handler = BytesHandler(image_data)
        bytes_per_pixel = 3
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            r_byte = bytes_handler.get_bytes(read_offset, 1)
            g_byte = bytes_handler.get_bytes(read_offset + 1, 1)
            b_byte = bytes_handler.get_bytes(read_offset + 2, 1)
            single_pixel_data = r_byte + g_byte + b_byte + b"\xFF"
            converted_raw_data += single_pixel_data
            read_offset += bytes_per_pixel

        return converted_raw_data

    # EA Image type 127
    def convert_bgr888_to_rgba8888(self, image_data: bytes) -> bytes:
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

    # EA Image type 2, 93, 115
    def convert_8bit_rgba8888pal_to_rgba8888(self, image_data: bytes, palette_data: bytes) -> bytes:
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
            if len(single_pixel_data) != 4:
                logger.error("[1] Wrong single pixel data size!")
                return b""
            converted_raw_data += single_pixel_data

        return converted_raw_data

    # EA Image type 1, 92, 119
    # TODO - fix this, it is pixelated after decoding
    def convert_4bit_rgba8888pal_to_rgba8888(self, image_data: bytes, palette_data: bytes) -> bytes:
        converted_raw_data = b""
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        bytes_per_palette_pixel = 4
        read_offset = 0
        for i in range(int((len(image_data)))):
            read_value = image_handler.get_bytes(read_offset, 1)
            read_value_int = struct.unpack("B", read_value)[0]
            val_str = bin(read_value_int).lstrip("0b").zfill(8)
            uint4_str1 = val_str[0:4]
            palette_index1 = int(uint4_str1, 2)
            uint4_str2 = val_str[4:8]
            palette_index2 = int(uint4_str2, 2)
            read_offset += 1

            palette_read_offset = palette_index1 * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            b_byte = palette_handler.get_bytes(palette_read_offset + 2, 1)
            a_byte = palette_handler.get_bytes(palette_read_offset + 3, 1)
            pixel_data1 = r_byte + g_byte + b_byte + a_byte
            converted_raw_data += pixel_data1

            palette_read_offset = palette_index2 * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            b_byte = palette_handler.get_bytes(palette_read_offset + 2, 1)
            a_byte = palette_handler.get_bytes(palette_read_offset + 3, 1)
            pixel_data2 = r_byte + g_byte + b_byte + a_byte
            converted_raw_data += pixel_data2

        return converted_raw_data

    # EA Image type 64
    def convert_4bit_rgba5551pal_to_rgba8888(self, image_data: bytes, palette_data: bytes) -> bytes:
        converted_raw_data = b""
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        bytes_per_palette_pixel = 2
        read_offset = 0
        for i in range(int((len(image_data)))):
            read_value = image_handler.get_bytes(read_offset, 1)
            read_value_int = struct.unpack("B", read_value)[0]
            val_str = bin(read_value_int).lstrip("0b").zfill(8)
            uint4_str1 = val_str[0:4]
            palette_index1 = int(uint4_str1, 2)
            uint4_str2 = val_str[4:8]
            palette_index2 = int(uint4_str2, 2)
            read_offset += 1

            palette_read_offset = palette_index1 * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            pixel_data1 = r_byte + g_byte
            pixel_data1_int = struct.unpack("<H", pixel_data1)[0]
            out_pixel1_int = self._unpack_2bytes_color_rgbp5551(pixel_data1_int, False)
            single_pixel_data1 = struct.pack(">I", out_pixel1_int)
            converted_raw_data += single_pixel_data1

            palette_read_offset = palette_index2 * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            pixel_data2 = r_byte + g_byte
            pixel_data2_int = struct.unpack("<H", pixel_data2)[0]
            out_pixel2_int = self._unpack_2bytes_color_rgbp5551(pixel_data2_int, False)
            single_pixel_data2 = struct.pack(">I", out_pixel2_int)
            converted_raw_data += single_pixel_data2

        return converted_raw_data

    # EA Image 65
    def convert_rgba5551pal_to_rgba8888(self, image_data: bytes, palette_data: bytes) -> bytes:
        converted_raw_data = b""
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        bytes_per_pixel = 1
        bytes_per_palette_pixel = 2
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            palette_index = image_handler.get_bytes(read_offset, 1)
            palette_index_int = struct.unpack("B", palette_index)[0]
            read_offset += bytes_per_pixel

            input_pixel: bytes = palette_handler.get_bytes(palette_index_int * bytes_per_palette_pixel, 2)
            input_pixel_int = struct.unpack("<H", input_pixel)[0]
            out_pixel_int = self._unpack_2bytes_color_rgbp5551(input_pixel_int, False)
            single_pixel_data = struct.pack(">I", out_pixel_int)
            converted_raw_data += single_pixel_data

        return converted_raw_data

    # EA Image type 96
    def pillow_convert_dxt1_to_rgba8888(self, image_data: bytes, img_width: int, img_height: int) -> bytes:
        pil_img = Image.frombuffer(
            "RGBA",
            (img_width, img_height),
            image_data,
            "bcn",
            1,  # 1 = DXT1 = BC1
            "",
        )
        return pil_img.tobytes()

    # EA Image type 97
    def pillow_convert_dxt3_to_rgba8888(self, image_data: bytes, img_width: int, img_height: int) -> bytes:
        pil_img = Image.frombuffer(
            "RGBA",
            (img_width, img_height),
            image_data,
            "bcn",
            2,  # 2 = DXT3 = BC2
            "",
        )
        return pil_img.tobytes()

    # EA Image type 123
    def convert_8bit_rgb888pal_to_rgba8888(self, image_data: bytes, palette_data: bytes) -> bytes:
        converted_raw_data = b""
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        bytes_per_pixel = 1
        bytes_per_palette_pixel = 3
        read_offset = 0
        for i in range(int(len(image_data) / bytes_per_pixel)):
            palette_index = image_handler.get_bytes(read_offset, 1)
            palette_index_int = struct.unpack("B", palette_index)[0]
            read_offset += bytes_per_pixel

            palette_read_offset = palette_index_int * bytes_per_palette_pixel
            r_byte = palette_handler.get_bytes(palette_read_offset, 1)
            g_byte = palette_handler.get_bytes(palette_read_offset + 1, 1)
            b_byte = palette_handler.get_bytes(palette_read_offset + 2, 1)
            a_byte = b"\xFF"
            single_pixel_data = r_byte + g_byte + b_byte + a_byte
            if len(single_pixel_data) != 4:
                logger.error("[2] Wrong single pixel data size!")
                return b""
            converted_raw_data += single_pixel_data

        return converted_raw_data

    # NEW LOGIC #

    def _decode_rgb565_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = ((pixel_int >> 11) & 0x1F) * 0xFF // 0x1F
        p[1] = ((pixel_int >> 5) & 0x3F) * 0xFF // 0x3F
        p[2] = ((pixel_int >> 0) & 0x1F) * 0xFF // 0x1F
        p[3] = 0xFF
        return p

    def _decode_i8_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = pixel_int
        p[1] = pixel_int
        p[2] = pixel_int
        p[3] = 0xFF
        return p

    data_formats = {
        # image_format: (decode_function, struct_format, bytes_per_pixel)
        "rgb565": (_decode_rgb565_pixel, "<H", 2),
        "i8": (_decode_i8_pixel, "<B", 1),
    }

    def _decode_generic(self, image_data: bytes, img_width: int, img_height: int, image_format: tuple) -> bytes:
        decode_function, struct_format, bytes_per_pixel = image_format
        image_handler = BytesHandler(image_data)
        texture_data = bytearray(img_width * img_height * 4)
        read_offset = 0
        for i in range(img_width * img_height):
            image_pixel: bytes = image_handler.get_bytes(read_offset, bytes_per_pixel)
            pixel_int: int = struct.unpack(struct_format, image_pixel)[0]
            read_offset += bytes_per_pixel
            texture_data[i * 4 : (i + 1) * 4] = decode_function(self, pixel_int)  # noqa
        return texture_data

    # EA Image Type 88
    def convert_rgb565_to_rgba8888(self, image_data: bytes, img_width: int, img_height: int) -> bytes:
        return self._decode_generic(image_data, img_width, img_height, self.data_formats["rgb565"])

    # # EA Image Type 115
    # def convert_i8_to_rgba8888(self, image_data: bytes, img_width: int, img_height: int) -> bytes:
    #     return self._decode_generic(image_data, img_width, img_height, self.data_formats["i8"])
