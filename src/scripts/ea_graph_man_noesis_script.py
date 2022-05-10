from inc_noesis import *
import struct

# EA Graphics Manager Noesis script
# Created by Bartlomiej Duda (Ikskoks)
# License: GPL-3.0 License
# This script is a part of the "EA Graphics Manager"
# More info here: https://github.com/bartlomiejduda/EA-Graphics-Manager


# This script is still in development.
# It may have some bugs. Some image types may be not supported.

SCRIPT_VERSION = "0.0.2"
SCRIPT_LAST_UPDATE = "11.05.2022"


debug_mode_enabled = True
is_image_twiddled = False


def registerNoesisTypes():
    handle = noesis.register("EA SSH FILES", ".ssh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA XSH FILES", ".xsh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)

    handle = noesis.register("EA MSH FILES", ".msh")
    noesis.setHandlerTypeCheck(handle, ea_image_check_type)
    noesis.setHandlerLoadRGBA(handle, ea_image_load)
    if debug_mode_enabled:
        noesis.logPopup()
    return 1


def ea_image_check_type(file_data):
    bs = NoeBitStream(file_data)
    signature = bs.readBytes(4).decode("UTF8")
    if (
            signature != "SHPS"      # SSH / SHPS
            and signature != "SHPX"  # XSH / SHPX
    ):
        return 0
    return 1


# bs = NoeBitStream(ea_image_file_data)
# bs = NoeBitStream(data, NOE_BIGENDIAN)
# bs.readBits(1)
# bs.readUByte()
# bs.readUShort()
# bs.readShort()
# bs.readUInt()
# bs.readBytes(size_to_read)
# curr_off = bs.tell()
# noeUnpack("b"...

def get_uint24(in_bytes, endianess):
    if endianess == "<":
        result = struct.unpack(endianess + "I", in_bytes + b"\x00")[0]
    else:
        result = struct.unpack(endianess + "I", b"\x00" + in_bytes)[0]
    return result


def ea_image_load(ea_image_file_data, tex_list):
    print("EA_GRAPH_MAN script v", SCRIPT_VERSION, " (", SCRIPT_LAST_UPDATE, ")")
    bs = NoeBitStream(ea_image_file_data)
    base_name = rapi.getInputName().split('\\')[-1].split('.')[0]
    print("base_name: ", base_name)

    # header parsing
    signature = bs.readBytes(4).decode("UTF8")  # e.g. "SHPS"
    total_file_size = bs.readUInt()
    number_of_entries = bs.readUInt()
    directory_id = bs.readBytes(4).decode("UTF8")  # e.g. "G354", "G264" etc.

    # directory parsing
    entry_tags_list = []
    entry_offsets_list = []
    for i in range(number_of_entries):
        entry_tags_list.append(bs.readUInt())
        entry_offsets_list.append(bs.readUInt())

    # image data parsing
    for i in range(number_of_entries):
        bs.seek(entry_offsets_list[i], NOESEEK_ABS)  # go to entry offset

        entry_type = bs.readUByte()
        pixel_total_size = get_uint24(bs.readBytes(3), "<")
        print("entry_type: ", entry_type)
        print("pixel_total_size: ", pixel_total_size)

        byte_per_pixel = entry_type - 1  # TODO

        img_width = bs.readUShort()
        img_height = bs.readUShort()
        bs.seek(8, NOESEEK_REL)  # skip reading XY coordinates


        if entry_type == 2:
            pass  # TODO
        else:
            message = "Entry type " + str(entry_type) + " is not supported!"
            noesis.messagePrompt(message)
            return 0


    print("\n")
    return 1
