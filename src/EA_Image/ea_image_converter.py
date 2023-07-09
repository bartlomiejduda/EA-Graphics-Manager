import struct

from src.EA_Image.Bmp import BmpImg


class EaImageConverter:

    def __init__(self):
        pass

    def convert_type_1_to_bmp(self, ea_dir_entry, ea_image):
        pass # TODO - implement this

    def convert_type_2_to_bmp(self, ea_dir_entry, ea_image):
        img_bpp = 8
        img_data = b""
        img_pal_data_size = len(ea_dir_entry.bin_attachments_list[0].raw_data)
        img_pal_data = b""
        img_height = ea_dir_entry.h_height
        img_width = ea_dir_entry.h_width

        # skew fix
        read_count = 0
        skew_val = img_width % 4
        for _ in range(img_height):
            temp_row = b""
            for _ in range(img_width):
                pixel = struct.pack(
                    ea_image.f_endianess + "B", ea_dir_entry.raw_data[read_count]
                )
                read_count += 1
                temp_row += pixel
            if skew_val == 1:
                temp_row += b"\x00\x00"
            elif skew_val == 2:
                temp_row += b"x\00"

            img_data += temp_row

        # missing pixels fix
        img_size_calc = img_height * img_width
        diff = (
                       ea_dir_entry.h_size_of_the_block - ea_dir_entry.header_size
               ) - img_size_calc
        for _ in range(diff):
            pixel = b"\x00"
            img_data += pixel

        # palette fix
        read_count = 0
        pal_range = int(img_pal_data_size / 4)
        for _ in range(pal_range):
            pal_entry1 = struct.pack(
                ea_image.f_endianess + "B",
                ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
            )
            read_count += 1
            pal_entry2 = struct.pack(
                ea_image.f_endianess + "B",
                ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
            )
            read_count += 1
            pal_entry3 = struct.pack(
                ea_image.f_endianess + "B",
                ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
            )
            read_count += 1
            pal_entry4 = struct.pack(
                ea_image.f_endianess + "B",
                ea_dir_entry.bin_attachments_list[0].raw_data[read_count],
            )
            read_count += 1
            img_pal_data += (
                    pal_entry3 + pal_entry2 + pal_entry1 + pal_entry4
            )  # RGBA swap

        bmp_object = BmpImg(
            img_width, img_height, img_bpp, img_data, img_pal_data
        )
        ea_dir_entry.img_convert_data = bmp_object.get_bmp_file_data()