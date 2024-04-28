"""
Copyright © 2024  Bartłomiej Duda
License: GPL-3.0 License
"""
import struct

from PIL import Image
from reversebox.common.logger import get_logger
from reversebox.io_files.bytes_handler import BytesHandler

from src.EA_Image.ea_image_formats import ImageFormats

logger = get_logger(__name__)

# fmt: off


# TODO - move it to ReverseBox
class EAImageDecoder:
    def __init__(self):
        pass

    def _decode_rgbx5551_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        p[0] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[2] = (b << 3) | (b >> 2)
        p[3] = 0xFF
        return p

    def _decode_xrgb1555_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        p[2] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[0] = (b << 3) | (b >> 2)
        p[3] = 0xFF
        return p

    def _decode_abgr1555_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        a = (pixel_int >> 15) & 0x1
        p[0] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[2] = (b << 3) | (b >> 2)
        p[3] = (0x00 if a == 0 else 0xFF)
        return p

    def _decode_xbgr1555_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        r = pixel_int & 0x1F
        g = (pixel_int >> 5) & 0x1F
        b = (pixel_int >> 10) & 0x1F
        p[0] = (r << 3) | (r >> 2)
        p[1] = (g << 3) | (g >> 2)
        p[2] = (b << 3) | (b >> 2)
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

    def _decode_argb8888_pixel(self, pixel_int: int) -> bytes:
        p = bytearray(4)
        p[2] = (pixel_int >> 0) & 0xff
        p[1] = (pixel_int >> 8) & 0xff
        p[0] = (pixel_int >> 16) & 0xff
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
        ImageFormats.RGB565: (_decode_rgb565_pixel, 16, _get_uint16),
        ImageFormats.RGB888: (_decode_rgb888_pixel, 24, _get_uint24),
        ImageFormats.BGR888: (_decode_bgr888_pixel, 24, _get_uint24),
        ImageFormats.ARGB4444: (_decode_argb4444_pixel, 16, _get_uint16),
        ImageFormats.RGBA4444: (_decode_rgba4444_pixel, 16, _get_uint16),
        ImageFormats.XRGB1555: (_decode_xrgb1555_pixel, 16, _get_uint16),
        ImageFormats.ABGR1555: (_decode_abgr1555_pixel, 16, _get_uint16),
        ImageFormats.XBGR1555: (_decode_xbgr1555_pixel, 16, _get_uint16),
        ImageFormats.ARGB8888: (_decode_argb8888_pixel, 32, _get_uint32),
    }

    indexed_data_formats = {
        # image_format: (decode_function, bits_per_pixel, palette_entry_size, palette_entry_read_function)
        ImageFormats.PAL4_RGBX5551: (_decode_rgbx5551_pixel, 4, 2, _get_uint16),
        ImageFormats.PAL4_RGB888: (_decode_rgb888_pixel, 4, 3, _get_uint24),
        ImageFormats.PAL4_RGBA8888: (_decode_rgba8888_pixel, 4, 4, _get_uint32),
        ImageFormats.PAL8_RGBX5551: (_decode_rgbx5551_pixel, 8, 2, _get_uint16),
        ImageFormats.PAL8_RGB888: (_decode_rgb888_pixel, 8, 3, _get_uint24),
        ImageFormats.PAL8_RGBA8888: (_decode_rgba8888_pixel, 8, 4, _get_uint32),
    }

    compressed_data_formats = {
        # image format: (decoder_name, decoder_arg)
        ImageFormats.DXT1: ("bcn", 1),
        ImageFormats.DXT3: ("bcn", 2)
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
        elif bits_per_pixel == 32:
            bytes_per_pixel = 4
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

    def _decode_compressed(self, image_data: bytes, img_width: int, img_height: int, image_format: tuple) -> bytes:
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

    def decode_image(self, image_data: bytes, img_width: int, img_height: int, image_format: ImageFormats, image_endianess: str = "little") -> bytes:
        return self._decode_generic(image_data, img_width, img_height, self.generic_data_formats[image_format], image_endianess)

    def decode_indexed_image(self, image_data: bytes, palette_data: bytes, img_width: int, img_height: int, image_format: ImageFormats, image_endianess: str = "little", palette_endianess: str = "little") -> bytes:
        return self._decode_indexed(image_data, palette_data, img_width, img_height, self.indexed_data_formats[image_format], image_endianess, palette_endianess)

    def decode_compressed_image(self, image_data: bytes, img_width: int, img_height: int, image_format: ImageFormats) -> bytes:
        return self._decode_compressed(image_data, img_width, img_height, self.compressed_data_formats[image_format])
