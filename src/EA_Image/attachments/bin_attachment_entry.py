"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

from src.EA_Image.dir_entry import DirEntry


class BinAttachmentEntry(DirEntry):
    entry_tags = {
        33: "palette 0x21",
        34: "palette 0x22",
        35: "palette 0x23",
        36: "palette 0x24",
        41: "palette 0x29",
        42: "palette 0x2A",
        45: "palette 0x2D",
        50: "palette 0x32",
        58: "palette 0x3A",
        59: "palette 0x3B",
        105: "metal bin",
        111: "comment",
        112: "img name",
        124: "hot spot",
    }

    def __init__(self, in_id, in_offset):
        self.id = in_id
        self.tag = None
        self.start_offset = in_offset
        self.end_offset = None
        self.raw_header = None
        self.raw_data_offset = None
        self.raw_data = None
        self.import_flag: bool = False

        self.h_record_id = None
        self.h_size_of_the_block = None

    def set_tag(self, in_entry_id):
        self.tag = self.entry_tags.get(
            in_entry_id,
            str(in_entry_id) + " | " + "0x%02X" % int(in_entry_id) + " | UNKNOWN_BIN_TYPE",
        )
