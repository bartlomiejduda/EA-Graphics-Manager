"""
Copyright © 2026  Bartłomiej Duda
License: GPL-3.0 License
"""


# class for holding mipmap data from EA Image
class EAMipmap:
    def __init__(self, width: int, height: int, size: int, raw_data: bytes, decoded_data: bytes):
        self.mipmap_width: int = width
        self.mipmap_height: int = height
        self.mipmap_size: int = size
        self.mipmap_raw_data: bytes = raw_data
        self.mipmap_decoded_data: bytes = decoded_data
