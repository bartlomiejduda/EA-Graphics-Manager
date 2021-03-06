import struct


def get_utf8_string(in_file, str_length):
    result = in_file.read(str_length).decode("utf8")
    return result


def get_uint8(in_file, endianess):
    result = struct.unpack(endianess + "B", in_file.read(1))[0]
    return result


def get_uint16(in_file, endianess):
    result = struct.unpack(endianess + "H", in_file.read(2))[0]
    return result


def get_uint12_uint4(in_file, endianess):
    bytes2 = in_file.read(2)
    val_int = struct.unpack(endianess + "H", bytes2)[0]
    val_str = bin(val_int).lstrip("0b").zfill(16)

    uint4_str = val_str[0:4]
    uint4_int = int(uint4_str, 2)

    uint12_str = val_str[4:16]
    uint12_int = int(uint12_str, 2)

    out_list = [uint12_int, uint4_int]
    return out_list


def get_uint24(in_file, endianess):
    if endianess == "<":
        result = struct.unpack(endianess + "I", in_file.read(3) + b"\x00")[0]
    else:
        result = struct.unpack(endianess + "I", b"\x00" + in_file.read(3))[0]
    return result


def get_uint32(in_file, endianess):
    result = struct.unpack(endianess + "L", in_file.read(4))[0]
    return result


def get_uint64(in_file, endianess):
    result = struct.unpack(endianess + "Q", in_file.read(8))[0]
    return result
