import struct

from inc_noesis import *

# EA Graphics Manager Noesis script
# Created by Bartlomiej Duda (Ikskoks)
# License: GPL-3.0 License
# This script is a part of the "EA Graphics Manager"
# More info here: https://github.com/bartlomiejduda/EA-Graphics-Manager


# This script is still in development.
# It may have some bugs. Some image types may be not supported.

SCRIPT_VERSION = "0.4"
SCRIPT_LAST_UPDATE = "15.11.2023"

# fmt: off
debug_mode_enabled = True


def registerNoesisTypes():
    handle = noesis.register("EA SSH (PS2) FILES", ".ssh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA XSH (XBOX) FILES", ".xsh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA MSH (PSP) FILES", ".msh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA FSH (PC) FILES", ".fsh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA PSH (PS1) FILES", ".psh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA GSH (WII) FILES", ".gsh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    if debug_mode_enabled:
        noesis.logPopup()
    return 1


def ea_image_check_type(file_data):
    bs = NoeBitStream(file_data)
    signature = bs.readBytes(4).decode("UTF8")
    if (
            signature != "SHPS"      # SSH (PS2)
            and signature != "SHPX"  # XSH (XBOX))
            and signature != "SHPI"  # FSH (PC)
            and signature != "SHPP"  # PSH (PS1)
            and signature != "SHPM"  # MSH (PSP)
            and signature != "SHPG"  # GSH (WII)
    ):
        return 0
    return 1


def get_uint24(in_bytes, endianess):
    if endianess == "<":
        result = struct.unpack(endianess + "I", in_bytes + b"\x00")[0]
    else:
        result = struct.unpack(endianess + "I", b"\x00" + in_bytes)[0]
    return result


def calculate_padding_len(in_len):
    div = 16
    padding_val = (div - (in_len % div)) % div
    return padding_val


PALETTE_TYPES = (33, 34, 35, 36, 41, 42, 45, 59)


def ea_image_load(ea_image_file_data, tex_list):
    print("EA_GRAPH_MAN script v", SCRIPT_VERSION, " (", SCRIPT_LAST_UPDATE, ")")
    bs = NoeBitStream(ea_image_file_data)
    base_name = rapi.getInputName().split('\\')[-1].split('.')[0]
    print("base_name: ", base_name)

    # header parsing
    bs.readBytes(4).decode("UTF8")  # signature, e.g. "SHPS"
    bs.readUInt()  # total file size
    number_of_entries = bs.readUInt()
    bs.readBytes(4).decode("UTF8")  # directory ID, e.g. "G354", "G264" etc.

    # directory parsing
    entry_tags_list = []
    entry_offsets_list = []
    for i in range(number_of_entries):
        entry_tags_list.append(bs.readUInt())
        entry_offsets_list.append(bs.readUInt())

    # image data parsing
    for i in range(number_of_entries):
        bs.seek(entry_offsets_list[i], NOESEEK_ABS)  # go to entry offset

        block_offset = bs.tell()
        entry_type = bs.readUByte()
        pixel_total_size = get_uint24(bs.readBytes(3), "<")

        print("\n\n###### ENTRY " + str(i+1) + " ###########")
        print("entry_type: ", entry_type)
        print("pixel_total_size: ", pixel_total_size)

        img_width = bs.readUShort()
        img_height = bs.readUShort()
        bs.seek(8, NOESEEK_REL)  # skip reading XY coordinates

        # here starts reading image data


        # 4-bit image with palette
        # e.g. Medal of Honor Frontline (PS2)
        if entry_type == 1:
            bits_per_pixel = 4
            pixel_size = img_width * img_height // 2
            pixel_data = bs.readBytes(pixel_size)

            bytes_per_palette_pixel = 4
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            print("palette size: ", palette_size)

            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 1 END


        # 8-bit image with palette
        # e.g. MVP Baseball 2005 (PS2)
        elif entry_type == 2:
            type2_decode_mode = 1   # 0 - standard
                                    # 1 - PS2 SHIFT

            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            print("img_height: ", img_height)
            print("img_width: ", img_width)
            print("pixel_size: ", pixel_size)
            print("after_pixel_offset: ", bs.tell())
            bs.seek(block_offset + pixel_total_size, NOESEEK_ABS)  # skip padding

            bytes_per_palette_pixel = 4
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)

            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            print("palette_size: ", palette_size)
            palette_data = bs.readBytes(palette_size)

            if type2_decode_mode == 0:
                pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                    "r8 g8 b8 a8")
            elif type2_decode_mode == 1:
                pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                    "r8 g8 b8 a8", noesis.DECODEFLAG_PS2SHIFT)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 2 END



        # 16-bit r5g5b5a1
        # e.g. Cricket 2007 (PS2)
        elif entry_type == 3:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 3 END


        # 24-bit r8g8b8
        # e.g. Medal of Honor Frontline (PS2)
        elif entry_type == 4:
            bytes_per_pixel = 3
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r8 g8 b8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 4 END




        # 32-bit r8g8b8a8
        # e.g. Medal of Honor Frontline (PS2)
        elif entry_type == 5:
            bytes_per_pixel = 4
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 5 END


        # 4-bit image with 16-bit palette (R5G5B5P1)
        # e.g. NBA Live 97 (PS1)
        elif entry_type == 64:
            bits_per_pixel = 4
            pixel_size = img_width * img_height // 2
            pixel_data = bs.readBytes(pixel_size)

            bytes_per_palette_pixel = 2
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)

            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 64 END



        # 8-bit image with 15-bit palette (R5G5B5P1)
        # e.g. NBA Live 97 (PS1)
        elif entry_type == 65:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            print("img_height: ", img_height)
            print("img_width: ", img_width)
            print("pixel_size: ", pixel_size)
            print("after_pixel_offset: ", bs.tell())
            bs.seek(block_offset + pixel_total_size, NOESEEK_ABS)  # skip padding

            bytes_per_palette_pixel = 2
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)

            palette_total_size = get_uint24(bs.readBytes(3), "<")
            print("palette_total_size: ", palette_total_size)
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            print("palette_size: ", palette_size)
            print("palette_offset: ", bs.tell())
            palette_data = bs.readBytes(palette_size)

            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                    "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 65 END


        # 16-bit image without palette (R5G5B5P1)
        # e.g. NBA Live 97 (PS1)
        elif entry_type == 66:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 66 END



        # RGBA4444
        # e.g. FIFA 2006 (PSP)
        elif entry_type == 90:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r4 g4 b4 p4")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 90 END




        # RGBA8888
        # e.g. FIFA 14 (PSP)
        elif entry_type == 91:
            bytes_per_pixel = 4
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 90 END


        # 4-bit image with palette and PSP swizzling
        # e.g. Madden 08 (PSP)
        elif entry_type == 92:
            bits_per_pixel = 4
            pixel_size = (img_width * img_height) // 2
            pixel_data = bs.readBytes(pixel_size)
            print("img_height: ", img_height)
            print("img_width: ", img_width)
            print("pixel_size: ", pixel_size)
            bs.seek(block_offset + pixel_total_size, NOESEEK_ABS)  # skip padding

            bytes_per_palette_pixel = 4
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)

            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            print("palette_size: ", palette_size)
            print("palette_offset: ", bs.tell())
            palette_data = bs.readBytes(palette_size)

            pixel_data = rapi.imageUntwiddlePSP(pixel_data, img_width, img_height, bits_per_pixel)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 92 END



        # 8-bit image with palette and PSP swizzling
        # e.g. Madden 08 (PSP)
        elif entry_type == 93:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            print("img_height: ", img_height)
            print("img_width: ", img_width)
            print("pixel_size: ", pixel_size)
            bs.seek(block_offset + pixel_total_size, NOESEEK_ABS)  # skip padding

            bytes_per_palette_pixel = 4
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)

            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            print("palette_size: ", palette_size)
            print("palette_offset: ", bs.tell())
            palette_data = bs.readBytes(palette_size)

            pixel_data = rapi.imageUntwiddlePSP(pixel_data, img_width, img_height, bits_per_pixel)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 93 END



        # DXT1, 4-bit
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 96:
            pixel_size = (img_width * img_height) // 2
            print("pixel_size: ", pixel_size, " img_width: ", img_width, " img_height: ", img_height)
            print("pixel_data_offset: ", bs.tell())
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeDXT(pixel_data, img_width, img_height, noesis.FOURCC_DXT1)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 96 END




        # DXT3, 8-bit
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 97:
            pixel_size = (img_width * img_height)
            print("pixel_size: ", pixel_size, " img_width: ", img_width, " img_height: ", img_height)
            print("pixel_data_offset: ", bs.tell())
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeDXT(pixel_data, img_width, img_height, noesis.FOURCC_DXT3)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 97 END



        # 8-bit RGB888PAL
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 123:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            bs.seek(block_offset + pixel_total_size, NOESEEK_ABS)  # skip padding

            bytes_per_palette_pixel = 3
            palette_type = bs.readUByte()
            print("palette_type:", palette_type)

            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)

            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel,
                                                "r8 g8 b8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 123 END




        # 32-bit A8R8G8B8
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 125:
            bytes_per_pixel = 4
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "b8 g8 r8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 125 END



        # 24-bit BGR888
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 127:
            bytes_per_pixel = 3
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "b8 g8 r8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 127 END




        elif entry_type in PALETTE_TYPES:
            message = "Palette type " + str(entry_type) + " is not supported!"
            print(message)
            return 0

        else:
            message = "Entry type " + str(entry_type) + " is not supported!"
            noesis.messagePrompt(message)
            return 0


    print("\n")
    return 1
