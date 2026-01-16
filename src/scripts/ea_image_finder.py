"""
Copyright © 2023-2026  Bartłomiej Duda
License: GPL-3.0 License
"""

import json
import os
import struct
from datetime import datetime
from typing import Optional

import pytz
from reversebox.common.logger import get_logger

# Script for finding valid EA image files.
# It generates JSON reports with details for each found file.


# globals
report_dict = {}
endianess = "<"  # "<" - little  / ">" - big
file_size_endianess = "<"
num_of_images_endianess = ">"
directory_endianess = ">"
logger = get_logger(__name__)


def parse_ea_image_file(file_path: str, file_name: str) -> Optional[dict]:
    logger.info("Parsing " + str(file_name) + "...")
    ea_image_file = None
    ea_image_dict = {}
    global report_dict
    ea_image_dict["file_name"] = file_name
    ea_image_dict["file_path"] = file_path
    ea_image_dict["is_error"] = "No error"

    try:
        ea_image_file = open(file_path, "rb")
        signature = ea_image_file.read(4).decode("utf8")
        if signature not in ("SHPI", "SHPP", "SHPS", "SHPX", "SHPM", "SHPG", "SHPA"):
            logger.info("File may be compressed! --> ", file_path)
            ea_image_dict["is_error"] = "Wrong signature error"
            return ea_image_dict
    except UnicodeDecodeError as error:
        ea_image_file.close()
        logger.info("File may be compressed! --> ", file_path, " Error: ", error)
        ea_image_dict["is_error"] = "UnicodeDecode error"
        return ea_image_dict

    try:
        ea_file_size = struct.unpack(file_size_endianess + "L", ea_image_file.read(4))[0]
        ea_image_dict["file_size"] = ea_file_size

        ea_image_file.seek(8)
        number_of_images = struct.unpack(num_of_images_endianess + "L", ea_image_file.read(4))[0]
        ea_image_dict["number_of_images"] = number_of_images
        ea_image_dict["EA_IMAGES"] = []

        # parse directory
        ea_image_file.seek(16)
        for i in range(number_of_images):
            entry_dict = {}
            entry_tag = ea_image_file.read(4).decode("utf8")
            entry_dict["entry_tag"] = entry_tag
            entry_offset = struct.unpack(directory_endianess + "L", ea_image_file.read(4))[0]
            entry_dict["entry_offset"] = entry_offset

            # parse data
            back_offset = ea_image_file.tell()
            ea_image_file.seek(entry_offset)
            entry_type = struct.unpack("B", ea_image_file.read(1))[0]
            entry_dict["entry_type"] = entry_type
            ea_image_file.seek(back_offset)

            entry_count = report_dict.get(".IMAGE_TYPE_" + str(entry_type), 0)
            entry_count += 1
            report_dict[".IMAGE_TYPE_" + str(entry_type)] = entry_count
            # parse data END

            ea_image_dict["EA_IMAGES"].append(entry_dict)

        ea_image_file.close()
        ea_image_dict["is_error"] = "NO"
        logger.info(f"SUCCESS. Finished parsing {file_name} file.")
        return ea_image_dict
    except Exception as error:
        logger.error(f"Error while parsing file. Error: {error}")
        ea_image_file.close()
        ea_image_dict["is_error"] = str(error)
        return ea_image_dict


def find_ea_files():
    logger.info("Starting find_ea_files...")
    search_directory_path = os.environ["SEARCH_DIRECTORY"]
    json_report_file_path = os.environ["JSON_REPORT_PATH"]

    global report_dict
    file_count = 0
    report_dict[".SEARCH_PATH"] = search_directory_path
    report_dict[".SEARCH_TIMESTAMP"] = str(datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%d.%m.%Y, %H:%M:%S"))

    # create report dictionaries
    report_dict["EA_FILES"] = []
    for root, dirs, files in os.walk(search_directory_path):
        for file in files:
            file_extension = file.split(".")[-1].upper()
            if file_extension in ("FSH", "SSH", "MSH", "XSH", "PSH", "GSH"):
                file_abs_path = os.path.join(root, file)
                ea_file_dict = parse_ea_image_file(file_abs_path, file)
                file_count += 1
                report_dict["EA_FILES"].append(ea_file_dict)

    # filter data in reports
    logger.info("Starting data filters logic...")
    temp_ea_files_list = []
    for ea_file_entry in report_dict["EA_FILES"]:
        if not ea_file_entry.get("file_size"):
            continue
        # if ea_file_entry["file_size"] > 285000 and ea_file_entry["number_of_images"] == 1:
        if ea_file_entry["file_size"] > 1:
            temp_ea_files_list.append(ea_file_entry)

    report_dict["EA_FILES"] = temp_ea_files_list

    # dump report to files
    logger.info("Dumping report to files...")
    with open(json_report_file_path, "w") as report_file:
        json.dump(report_dict, report_file, indent=4, sort_keys=True)

    logger.info("Finished find_ea_files...")


if __name__ == "__main__":
    logger.info("Starting ea_image_finder...")
    find_ea_files()
    logger.info("End of ea_image_finder...")
