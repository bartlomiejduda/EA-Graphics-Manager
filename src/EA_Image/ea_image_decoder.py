"""
Copyright © 2024  Bartłomiej Duda
License: GPL-3.0 License
"""
import struct

from PIL import Image
from reversebox.common.logger import get_logger
from reversebox.io_files.bytes_handler import BytesHandler

logger = get_logger(__name__)

# fmt: off


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

    def _unpack_2bytes_color_argb1555(self, value, use_alpha=True):
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

    def _unpack_2bytes_color_argb4444(self, byte1, byte2):
        r = (byte1 >> 4) * 16
        g = (byte1 & 15) * 16
        b = (byte2 >> 4) * 16
        a = (byte2 & 15) * 16
        return (r << 16) | (g << 8) | b | (a << 24)

    # EA Image type 125
    def convert_argb8888_to_rgba8888(self, image_data: bytes) -> bytes:
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

    # NEW LOGIC #

    def _decode_rgba5551_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        # a = (pixel_int >> 15) & 0x1
        p[0] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[2] = (b << 3) | (b >> 2)
        p[3] = 0xFF
        return p

    def _decode_argb1555_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        # a = (pixel_int >> 15) & 0x1
        p[2] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[0] = (b << 3) | (b >> 2)
        p[3] = 0xFF
        return p

    def _decode_rgb565_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = ((pixel_int >> 11) & 0x1F) * 0xFF // 0x1F
        p[1] = ((pixel_int >> 5) & 0x3F) * 0xFF // 0x3F
        p[2] = ((pixel_int >> 0) & 0x1F) * 0xFF // 0x1F
        p[3] = 0xFF
        return p

    def _decode_rgb888_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = (pixel_int >> 0) & 0xff
        p[1] = (pixel_int >> 8) & 0xff
        p[2] = (pixel_int >> 16) & 0xff
        p[3] = 0xFF
        return p

    def _decode_bgr888_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = (pixel_int >> 16) & 0xff
        p[1] = (pixel_int >> 8) & 0xff
        p[2] = (pixel_int >> 0) & 0xff
        p[3] = 0xFF
        return p

    def _decode_rgba8888_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[0] = (pixel_int >> 0) & 0xff
        p[1] = (pixel_int >> 8) & 0xff
        p[2] = (pixel_int >> 16) & 0xff
        p[3] = (pixel_int >> 24) & 0xff
        return p

    def _decode_argb4444_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        a = (pixel_int >> 12) & 0xff
        r = (pixel_int >> 8) & 0x0f
        g = (pixel_int >> 4) & 0x0f
        b = (pixel_int >> 0) & 0x0f

        p[0] = (r << 4) | (r >> 0)
        p[1] = (g << 4) | (g >> 0)
        p[2] = (b << 4) | (b >> 0)
        p[3] = (a << 4) | (a >> 0)
        return p

    def _decode_rgba4444_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        a = (pixel_int >> 12) & 0xff
        r = (pixel_int >> 8) & 0x0f
        g = (pixel_int >> 4) & 0x0f
        b = (pixel_int >> 0) & 0x0f

        p[0] = (b << 4) | (b >> 0)
        p[1] = (g << 4) | (g >> 0)
        p[2] = (r << 4) | (r >> 0)
        p[3] = (a << 4) | (a >> 0)
        return p

    def _get_uint16(self, in_bytes: bytes, endianess: str) -> int:
        result = struct.unpack(endianess + "H", in_bytes)[0]
        return result

    def _get_uint24(self, in_bytes: bytes, endianess: str) -> int:
        if endianess == "<":
            result = struct.unpack(endianess + "I", in_bytes + b"\x00")[0]
        elif endianess == ">":
            result = struct.unpack(endianess + "I", b"\x00" + in_bytes)[0]
        else:
            raise Exception("Wrong endianess!")
        return result

    def _get_uint32(self, in_bytes: bytes, endianess: str) -> int:
        result = struct.unpack(endianess + "I", in_bytes)[0]
        return result

    generic_data_formats = {
        # image_format: (decode_function, bits_per_pixel, image_entry_read_function)
        "rgb565": (_decode_rgb565_pixel, 16, _get_uint16),
        "rgb888": (_decode_rgb888_pixel, 24, _get_uint24),
        "bgr888": (_decode_bgr888_pixel, 24, _get_uint24),
        "argb4444": (_decode_argb4444_pixel, 16, _get_uint16),
        "rgba4444": (_decode_rgba4444_pixel, 16, _get_uint16),
        "argb1555": (_decode_argb1555_pixel, 16, _get_uint16),
    }

    indexed_data_formats = {
        # image_format: (decode_function, bits_per_pixel, palette_entry_size, palette_entry_read_function)
        "pal4_rgba5551": (_decode_rgba5551_pixel, 4, 2, _get_uint16),
        "pal4_rgb888": (_decode_rgb888_pixel, 4, 3, _get_uint24),
        "pal4_rgba8888": (_decode_rgba8888_pixel, 4, 4, _get_uint32),
        "pal8_rgba5551": (_decode_rgba5551_pixel, 8, 2, _get_uint16),
        "pal8_rgb888": (_decode_rgb888_pixel, 8, 3, _get_uint24),
        "pal8_rgba8888": (_decode_rgba8888_pixel, 8, 4, _get_uint32),
    }

    dxt_data_formats = {
        # image format: (decoder_name, decoder_arg)
        "dxt1": ("bcn", 1),
        "dxt3": ("bcn", 2)
    }

    def _get_endianess_format(self, endianess: str) -> str:
        if endianess == "little":
            endianess_format = "<"
        elif endianess == "big":
            endianess_format = ">"
        else:
            raise Exception("Wrong endianess!")
        return endianess_format

    def _decode_generic(self, image_data: bytes, img_width: int, img_height: int, image_format: tuple, image_endianess: str) -> bytes:
        decode_function, bits_per_pixel, image_entry_read_function = image_format
        image_handler = BytesHandler(image_data)
        texture_data = bytearray(img_width * img_height * 4)
        read_offset = 0
        image_endianess_format: str = self._get_endianess_format(image_endianess)

        if bits_per_pixel == 16:
            bytes_per_pixel = 2
            for i in range(len(image_data) // bytes_per_pixel):
                image_pixel: bytes = image_handler.get_bytes(read_offset, bytes_per_pixel)
                pixel_int: int = image_entry_read_function(self, image_pixel, image_endianess_format)
                read_offset += bytes_per_pixel
                texture_data[i * 4 : (i + 1) * 4] = decode_function(self, pixel_int)  # noqa
        elif bits_per_pixel == 24:
            bytes_per_pixel = 3
            for i in range(len(image_data) // bytes_per_pixel):
                image_pixel: bytes = image_handler.get_bytes(read_offset, bytes_per_pixel)
                pixel_int: int = image_entry_read_function(self, image_pixel, image_endianess_format)
                read_offset += bytes_per_pixel
                texture_data[i * 4: (i + 1) * 4] = decode_function(self, pixel_int)  # noqa
        else:
            raise Exception(f"Bpp {bits_per_pixel} not supported!")

        return texture_data

    def _decode_indexed(self, image_data: bytes, palette_data: bytes, img_width: int,
                        img_height: int, image_format: tuple, image_endianess: str, palette_endianess: str) -> bytes:
        decode_function, bits_per_pixel, palette_entry_size, palette_entry_read_function = image_format
        image_handler = BytesHandler(image_data)
        palette_handler = BytesHandler(palette_data)
        texture_data = bytearray(img_width * img_height * 4)
        image_offset = 0
        palette_offset = 0
        image_endianess_format: str = self._get_endianess_format(image_endianess)
        palette_endianess_format: str = self._get_endianess_format(palette_endianess)

        palette_data_ints = []
        for i in range(len(palette_data) // palette_entry_size):
            palette_entry = palette_handler.get_bytes(palette_offset, palette_entry_size)
            palette_entry_int = palette_entry_read_function(self, palette_entry, palette_endianess_format)
            palette_offset += palette_entry_size
            palette_data_ints.append(palette_entry_int)

        if bits_per_pixel == 16:
            for i in range(img_width * img_height):
                palette_index = image_handler.get_bytes(image_offset, 2)
                palette_index_int = struct.unpack(image_endianess_format + "H", palette_index)[0]
                texture_data[i * 4:(i + 1) * 4] = decode_function(self, palette_data_ints[palette_index_int])  # noqa
                image_offset += 2
        elif bits_per_pixel == 8:
            for i in range(img_width * img_height):
                palette_index = image_handler.get_bytes(image_offset, 1)
                palette_index_int = struct.unpack(image_endianess_format + "B", palette_index)[0]
                texture_data[i * 4:(i + 1) * 4] = decode_function(self, palette_data_ints[palette_index_int])  # noqa
                image_offset += 1
        elif bits_per_pixel == 4:
            for i in range(0, img_width * img_height, 2):
                palette_index = image_handler.get_bytes(image_offset, 1)
                palette_index_int = struct.unpack(image_endianess_format + "B", palette_index)[0]
                texture_data[i * 4:(i + 1) * 4] = decode_function(self, palette_data_ints[(palette_index_int >> 4) & 0xf])  # noqa
                texture_data[(i + 1) * 4:(i + 2) * 4] = decode_function(self, palette_data_ints[palette_index_int & 0xf])  # noqa
                image_offset += 1

        return texture_data

    def _decode_dxt(self, image_data: bytes, img_width: int, img_height: int, image_format: str) -> bytes:
        decoder_name, decoder_arg = image_format
        pil_img = Image.frombuffer(
            "RGBA",
            (img_width, img_height),
            image_data,
            decoder_name,
            decoder_arg,
            "",
        )
        return pil_img.tobytes()

    def decode_image(self, image_data: bytes, img_width: int, img_height: int, image_format: str, image_endianess: str = "little") -> bytes:
        return self._decode_generic(image_data, img_width, img_height, self.generic_data_formats[image_format], image_endianess)

    def decode_indexed_image(self, image_data: bytes, palette_data: bytes, img_width: int, img_height: int, image_format: str, image_endianess: str = "little", palette_endianess: str = "little") -> bytes:
        return self._decode_indexed(image_data, palette_data, img_width, img_height, self.indexed_data_formats[image_format], image_endianess, palette_endianess)

    def decode_dxt_image(self, image_data: bytes, img_width: int, img_height: int, image_format: str) -> bytes:
        return self._decode_dxt(image_data, img_width, img_height, self.dxt_data_formats[image_format])
