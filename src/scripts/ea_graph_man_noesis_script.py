import struct

from inc_noesis import *

# EA Graphics Manager Noesis script
# Created by Bartlomiej Duda (Ikskoks)
# License: GPL-3.0 License
# This script is a part of the "EA Graphics Manager"
# More info here: https://github.com/bartlomiejduda/EA-Graphics-Manager


# This script is still in development.
# It may have some bugs. Some image types may be not supported.

SCRIPT_VERSION = "0.6"
SCRIPT_LAST_UPDATE = "27.04.2024"

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
    signature = bs.readBytes(4).decode("UTF8")  # signature, e.g. "SHPS"
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

        data_block_offset = bs.tell()
        entry_type = bs.readUByte()
        data_block_total_size = get_uint24(bs.readBytes(3), "<")  # usually pixel data + 16-bytes header

        print("\n\n###### ENTRY " + str(i+1) + " ###########")
        print("entry_type: ", entry_type)
        print("data_block_offset: " + str(data_block_offset))
        print("data_block_total_size: ", data_block_total_size)

        img_width = bs.readUShort()
        img_height = bs.readUShort()
        bs.seek(8, NOESEEK_REL)  # skip reading XY coordinates

        # here starts reading image data


        # PAL4
        # e.g. Medal of Honor Frontline (PS2)
        if entry_type == 1:
            bits_per_pixel = 4
            pixel_size = img_width * img_height // 2
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 4
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 1 END



        # PAL8
        # e.g. MVP Baseball 2005 (PS2)
        elif entry_type == 2:
            type2_decode_mode = 1   # 0 - standard (very rare, e.g. NHL 2002 PS2)
                                    # 1 - PS2 palette swizzling (most games do this)
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 4
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
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



        # ABGR1555
        # e.g. Cricket 2007 (PS2)
        elif entry_type == 3:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r5 g5 b5 a1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 3 END



        # RGB888
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



        # RGBA8888
        # e.g. Medal of Honor Frontline (PS2)
        elif entry_type == 5:
            bytes_per_pixel = 4
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 5 END



        # PAL4_RGBP5551
        # e.g. NBA Live 97 (PS1)
        elif entry_type == 64:
            bits_per_pixel = 4
            pixel_size = img_width * img_height // 2
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 2
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 64 END



        # PAL8_RGBP5551
        # e.g. NBA Live 97 (PS1)
        elif entry_type == 65:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 2
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r5 g5 b5 p1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 65 END



        # RGBP5551
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



        # RGB888 + empty palette (?)
        # e.g. ReBoot (PS1)
        elif entry_type == 67:
            bytes_per_pixel = 3
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r8 g8 b8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 4 END



        # RGB565 (?)
        # e.g. Need For Speed: Undercover (PSP)
        elif entry_type == 88:
                bytes_per_pixel = 2
                pixel_size = img_width * img_height * bytes_per_pixel
                pixel_data = bs.readBytes(pixel_size)
                pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r5 g6 b5")

                texture_format = noesis.NOESISTEX_RGBA32
                texture_name = "%s_%d" % (base_name, i)
                tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
                # entry type 88 END



        # RGB565 (?)
        # e.g. FIFA 2006 (PSP)
        elif entry_type == 89:
                bytes_per_pixel = 2
                pixel_size = img_width * img_height * bytes_per_pixel
                pixel_data = bs.readBytes(pixel_size)
                pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r5 g6 b5")

                texture_format = noesis.NOESISTEX_RGBA32
                texture_name = "%s_%d" % (base_name, i)
                tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
                # entry type 89 END



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



        # RGBA8888 (can be PSP swizzled)
        # e.g. FIFA 14 (PSP)
        elif entry_type == 91:
            bytes_per_pixel = 4
            bits_per_pixel = 32
            img_mode = 0  # 0 - standard  / 1 - PSP swizzled (rare)
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            if img_mode == 1:
                pixel_data = rapi.imageUntwiddlePSP(pixel_data, img_width, img_height, bits_per_pixel)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 90 END



        # PAL4 PSP
        # e.g. Madden 08 (PSP)
        elif entry_type == 92:
            bits_per_pixel = 4
            pixel_size = (img_width * img_height) // 2
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 4
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageUntwiddlePSP(pixel_data, img_width, img_height, bits_per_pixel)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 92 END



        # PAL8 PSP
        # e.g. Madden 08 (PSP)
        elif entry_type == 93:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 4
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageUntwiddlePSP(pixel_data, img_width, img_height, bits_per_pixel)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 93 END



        # DXT1
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 96:
            pixel_size = (img_width * img_height) // 2
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeDXT(pixel_data, img_width, img_height, noesis.FOURCC_DXT1)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 96 END



        # DXT3
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 97:
            pixel_size = (img_width * img_height)
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeDXT(pixel_data, img_width, img_height, noesis.FOURCC_DXT3)

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry 97 END



        # ARGB4444
        # e.g. Need For Speed: Porsche Unleashed (PC)
        elif entry_type == 109:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "b4 g4 r4 a4")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 109 END



        # PAL8 (image and palette in one data block)
        # e.g. Need for Speed Carbon: Own the City (PSP/Zeebo)
        elif entry_type == 115:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            palette_data = bs.readBytes(1024)
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 115 END



        # PAL4 (image and palette in one data block)
        # e.g. Need for Speed Carbon: Own the City (PSP/Zeebo)
        elif entry_type == 119:
            bits_per_pixel = 4
            pixel_size = img_width * img_height // 2
            palette_data = bs.readBytes(64)
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8 a8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 119 END



        # RGB565
        # e.g. Need For Speed: Porsche Unleashed (PC)
        elif entry_type == 120:
                bytes_per_pixel = 2
                pixel_size = img_width * img_height * bytes_per_pixel
                pixel_data = bs.readBytes(pixel_size)
                pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "b5 g6 r5")

                texture_format = noesis.NOESISTEX_RGBA32
                texture_name = "%s_%d" % (base_name, i)
                tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
                # entry type 120 END



        # PAL8_RGB888
        # e.g. SimCity 4 Deluxe (PC)
        elif entry_type == 123:
            bits_per_pixel = 8
            bytes_per_pixel = 1
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            bytes_per_palette_pixel = 3
            bs.seek(data_block_offset + data_block_total_size, NOESEEK_ABS)  # skip padding
            palette_type = bs.readUByte()
            palette_total_size = get_uint24(bs.readBytes(3), "<")
            palette_width = bs.readUShort()
            palette_height = bs.readUShort()
            bs.seek(8, NOESEEK_REL)  # skip unknown bytes
            palette_size = palette_width * palette_height * bytes_per_palette_pixel
            palette_data = bs.readBytes(palette_size)
            pixel_data = rapi.imageDecodeRawPal(pixel_data, palette_data, img_width, img_height, bits_per_pixel, "r8 g8 b8")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 123 END



        # ARGB8888
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



        # ARGB1555
        # e.g. Need For Speed III: Hot Pursuit (PC)
        elif entry_type == 126:
            bytes_per_pixel = 2
            pixel_size = img_width * img_height * bytes_per_pixel
            pixel_data = bs.readBytes(pixel_size)
            pixel_data = rapi.imageDecodeRaw(pixel_data, img_width, img_height, "b5 g5 r5 a1")

            texture_format = noesis.NOESISTEX_RGBA32
            texture_name = "%s_%d" % (base_name, i)
            tex_list.append(NoeTexture(texture_name, img_width, img_height, pixel_data, texture_format))
            # entry type 126 END



        # RGB888
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
# fmt: on
