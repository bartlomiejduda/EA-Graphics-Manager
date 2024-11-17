# -*- coding: utf-8 -*-

"""
Copyright © 2024  Bartłomiej Duda
License: GPL-3.0 License
"""
import io
import os
import subprocess
import tkinter as tk
import traceback
from configparser import ConfigParser
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

from PIL import Image, ImageTk
from reversebox.common.common import get_file_extension, get_file_extension_uppercase
from reversebox.common.logger import get_logger
from reversebox.compression.compression_refpack import RefpackHandler
from reversebox.image.pillow_wrapper import PillowWrapper

from src.EA_Image import ea_image_main
from src.EA_Image.bin_attachment_entries import PaletteEntry
from src.EA_Image.constants import (
    CONVERT_IMAGES_SUPPORTED_TYPES,
    IMPORT_IMAGES_SUPPORTED_TYPES,
    NEW_SHAPE_ALLOWED_SIGNATURES,
    OLD_SHAPE_ALLOWED_SIGNATURES,
    PALETTE_TYPES,
)
from src.EA_Image.ea_image_encoder import encode_ea_image
from src.GUI.about_window import AboutWindow
from src.GUI.GUI_entry_preview import GuiEntryPreview
from src.GUI.GUI_menu import GuiMenu
from src.GUI.GUI_tab_controller import GuiTabController
from src.GUI.GUI_treeview import GuiTreeView

# default app settings
WINDOW_HEIGHT = 460
WINDOW_WIDTH = 950
MIN_WINDOW_HEIGHT = WINDOW_HEIGHT
MIN_WINDOW_WIDTH = WINDOW_WIDTH
MAX_WINDOW_HEIGHT = WINDOW_HEIGHT
MAX_WINDOW_WIDTH = WINDOW_WIDTH


logger = get_logger(__name__)


# fmt: off

class EAManGui:
    def __init__(self, master, in_version_num, in_main_directory):
        logger.info("GUI init...")
        self.master = master
        self.VERSION_NUM = in_version_num
        self.MAIN_DIRECTORY = in_main_directory
        master.title("EA GRAPHICS MANAGER " + in_version_num)
        master.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        master.maxsize(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT)
        master.resizable(width=0, height=0)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.tree_rclick_popup = None
        self.icon_path = self.MAIN_DIRECTORY + "\\data\\img\\ea_icon.ico"
        self.checkmark_path = self.MAIN_DIRECTORY + "\\data\\img\\checkmark.png"
        self.checkmark_image = None

        try:
            self.master.iconbitmap(self.icon_path)
        except tk.TclError:
            logger.error(f"Can't load the icon file from {self.icon_path}")

        self.allowed_filetypes = [
            (
                "EA Graphics files",
                ["*.fsh", "*.psh", "*.ssh", "*.msh", "*.xsh", "*.gsh", "*.qfs", "*.ash"],
            ),
            ("All files", ["*.*"]),
        ]

        self.allowed_import_image_filetypes = [
            (
                "Image files",
                ["*.dds", "*.png", "*.bmp"],
            ),
            ("All files", ["*.*"]),
        ]

        self.ea_image_id = 0
        self.opened_ea_images_count = 0
        self.opened_ea_images = []

        # main frame
        self.main_frame = tk.Frame(master, bg="#f0f0f0")
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # gui objects
        self.tree_view = GuiTreeView(self.main_frame, self)
        self.tab_controller = GuiTabController(self.main_frame, self)
        self.entry_preview = GuiEntryPreview(self.main_frame, self)
        self.menu = GuiMenu(self.master, self)
        self.loading_label = None

        # user config
        self.user_config = ConfigParser()
        self.user_config_file_name: str = "config.ini"
        self.user_config.add_section("config")
        self.user_config.set("config", "save_directory_path", "")
        self.user_config.set("config", "open_directory_path", "")
        if not os.path.exists(self.user_config_file_name):
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)

        self.user_config.read(self.user_config_file_name)
        try:
            self.current_save_directory_path = self.user_config.get("config", "save_directory_path")
            self.current_open_directory_path = self.user_config.get("config", "open_directory_path")
        except Exception as error:
            logger.error(f"Error while loading user config: {error}")
            self.current_save_directory_path = ""
            self.current_open_directory_path = ""

    ######################################################################################################
    #                                             methods                                                #
    ######################################################################################################

    def _execute_old_shape_tab_logic(self):
        self.tab_controller.tab_controller_box.tab(0, state="normal")
        self.tab_controller.tab_controller_box.tab(1, state="disabled")
        self.tab_controller.tab_controller_box.select(0)

    def _execute_new_shape_tab_logic(self):
        self.tab_controller.tab_controller_box.tab(0, state="disabled")
        self.tab_controller.tab_controller_box.tab(1, state="normal")
        self.tab_controller.tab_controller_box.select(1)

    def treeview_widget_select(self, event):
        item_iid = self.tree_view.treeview_widget.identify_row(event.y)

        if item_iid == "":
            return  # quit if nothing is selected

        item_id = item_iid.split("_")[0]

        ea_img = self.tree_view.tree_man.get_object(item_id, self.opened_ea_images)

        # set text for header
        if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_sign, ea_img.sign)
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_f_size, ea_img.total_f_size)
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_dir_id, ea_img.format_version)
            self._execute_old_shape_tab_logic()
        elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_sign, ea_img.sign)
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_f_size, ea_img.total_f_size)
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_header_and_toc_size, ea_img.header_and_toc_size)
            self._execute_new_shape_tab_logic()

        # set text for dir entry
        if "direntry" in item_iid and "binattach" not in item_iid:
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, item_iid)

            if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_rec_type, ea_dir.get_entry_type())
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_size_of_the_block, ea_dir.h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_mipmaps_count, ea_dir.h_mipmaps_count)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_width, ea_dir.h_width)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_height, ea_dir.h_height)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_x, ea_dir.h_center_x)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_y, ea_dir.h_center_y)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_left_x, ea_dir.h_default_x_position)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_top_y, ea_dir.h_default_y_position)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_header_offset, ea_dir.h_entry_header_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_offset, ea_dir.raw_data_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_size, ea_dir.raw_data_size)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_end_offset, ea_dir.h_entry_end_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_record_id_masked, ea_dir.h_record_id_masked)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_img_compression_masked, ea_dir.h_is_image_compressed_masked)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag1_referenced, ea_dir.h_flag1_referenced)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag2_swizzled, ea_dir.h_flag2_swizzled)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag3_transposed, ea_dir.h_flag3_transposed)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag4_reserved, ea_dir.h_flag4_reserved)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_image_bpp, ea_dir.h_image_bpp)
                self._execute_old_shape_tab_logic()
            elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_rec_type, ea_dir.get_entry_type())
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_size_of_the_block, ea_dir.h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_width, ea_dir.h_width)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_height, ea_dir.h_height)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_left_x, ea_dir.h_default_x_position)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_top_y, ea_dir.h_default_y_position)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_image_bpp, ea_dir.h_image_bpp)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_mipmaps_count, ea_dir.new_shape_number_of_mipmaps)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_int, ea_dir.new_shape_flags)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_hex_str, ea_dir.new_shape_flags_hex_str)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_header_offset, ea_dir.h_entry_header_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_offset, ea_dir.raw_data_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_end_offset, ea_dir.h_entry_end_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_size, ea_dir.raw_data_size)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_new_format, ea_dir.new_shape_flag_new_format)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_compressed, ea_dir.new_shape_flag_compressed)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_swizzled, ea_dir.new_shape_flag_swizzled)
                self._execute_new_shape_tab_logic()

            # image preview logic START
            try:
                self.entry_preview.preview_instance.destroy()
            except Exception:
                pass

            if ea_dir.is_img_convert_supported:
                self.entry_preview.init_image_preview_logic(ea_dir, item_iid)

            else:
                self.entry_preview.init_image_preview_not_supported_logic()
            # image preview logic END

        # set text and preview for bin attach entry
        elif "binattach" in item_iid:
            dir_iid = item_iid.split("_binattach")[0]
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, dir_iid)
            bin_attach = self.tree_view.tree_man.get_object_bin_attach(ea_dir, item_iid)

            if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_rec_type, bin_attach.get_entry_type())
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_size_of_the_block, bin_attach.h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_mipmaps_count, "")

                if isinstance(bin_attach, PaletteEntry):
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_width, bin_attach.h_width)
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_height, bin_attach.h_height)
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_x, bin_attach.h_center_x)
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_y, bin_attach.h_center_y)
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_left_x, bin_attach.h_default_x_position)
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_top_y, bin_attach.h_default_y_position)
                else:
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_width, "")
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_height, "")
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_x, "")
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_y, "")
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_left_x, "")
                    self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_top_y, "")

                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_header_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_size, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_end_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_record_id_masked, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_img_compression_masked, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag1_referenced, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag2_swizzled, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag3_transposed, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag4_reserved, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_image_bpp, "")
                self._execute_old_shape_tab_logic()
            if ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_rec_type, bin_attach.get_entry_type())
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_size_of_the_block, bin_attach.h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_width, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_height, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_left_x, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_top_y, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_image_bpp, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_mipmaps_count, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_int, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_hex_str, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_header_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_end_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_size, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_new_format, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_compressed, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_swizzled, "")
                self._execute_new_shape_tab_logic()

            # bin attachment preview logic START
            try:
                self.entry_preview.preview_instance.destroy()
            except Exception:
                pass

            if bin_attach.h_record_id in PALETTE_TYPES:  # palette types
                self.entry_preview.init_palette_preview_logic(bin_attach)
            else:
                self.entry_preview.init_binary_preview_logic(bin_attach)
            # bin attachment preview logic END

        else:
            if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_rec_type, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_size_of_the_block, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_mipmaps_count, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_width, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_height, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_x, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_y, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_left_x, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_top_y, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_header_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_size, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_end_offset, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_record_id_masked, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_img_compression_masked, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag1_referenced, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag2_swizzled, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag3_transposed, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag4_reserved, "")
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_image_bpp, "")
                self._execute_old_shape_tab_logic()
            elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_rec_type, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_size_of_the_block, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_width, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_height, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_left_x, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_top_y, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_image_bpp, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_mipmaps_count, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_int, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_hex_str, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_header_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_end_offset, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_size, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_new_format, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_compressed, "")
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_swizzled, "")
                self._execute_new_shape_tab_logic()

            try:
                self.entry_preview.preview_instance.destroy()
            except Exception:
                pass

        if event.num == 3:
            self.tree_view.treeview_widget.selection_set(item_iid)
            self.treeview_rightclick_popup(event, item_iid)

    def treeview_rightclick_popup(self, event, item_iid):
        # create right-click popup menu
        self.tree_rclick_popup = tk.Menu(self.master, tearoff=0)
        if "direntry" not in item_iid and "binattach" not in item_iid:
            self.tree_rclick_popup.add_command(
                label="Open in Explorer", command=lambda: self.treeview_rclick_open_in_explorer(item_iid)
            )
            self.tree_rclick_popup.add_command(label="Close File", command=lambda: self.treeview_rclick_close(item_iid))
            self.tree_rclick_popup.add_command(
                label="Save File As...", command=lambda: self.treeview_rclick_save_file_as(item_iid)
            )
            self.tree_rclick_popup.tk_popup(event.x_root, event.y_root, entry="0")
        elif "direntry" in item_iid and "binattach" not in item_iid:
            self.tree_rclick_popup.add_command(
                label="Export Raw Image Data",
                command=lambda: self.treeview_rclick_export_raw(item_iid),
            )
            self.tree_rclick_popup.add_command(
                label="Export Image as DDS/PNG/BMP", command=lambda: self.treeview_rclick_export_image(item_iid)
            )
            self.tree_rclick_popup.add_command(
                label="Import Image from DDS/PNG/BMP", command=lambda: self.treeview_rclick_import_image(item_iid)
            )
            self.tree_rclick_popup.tk_popup(event.x_root, event.y_root, entry="0")
        elif "direntry" in item_iid and "binattach" in item_iid:
            self.tree_rclick_popup.add_command(
                label="Export Raw Binary Data",
                command=lambda: self.treeview_rclick_export_raw(item_iid),
            )
            # self.tree_rclick_popup.add_command(label="Import Raw Binary Data")
            self.tree_rclick_popup.tk_popup(event.x_root, event.y_root, entry="0")
        else:
            logger.warning("Warning! Unsupported entry in right-click popup!")

    def treeview_rclick_close(self, item_iid):
        ea_img = self.tree_view.tree_man.get_object(item_iid, self.opened_ea_images)
        self.tree_view.treeview_widget.delete(item_iid)  # removing item from treeview

        if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_sign, "")
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_f_size, "")
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_obj_count, "")
            self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_dir_id, "")
            self._execute_old_shape_tab_logic()
        elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_sign, "")
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_f_size, "")
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_obj_count, "")
            self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_header_and_toc_size, "")
            self._execute_new_shape_tab_logic()

        del ea_img  # removing object from memory

    def treeview_rclick_save_file_as(self, item_iid):
        ea_img = self.tree_view.tree_man.get_object(item_iid, self.opened_ea_images)
        with open(ea_img.f_path, "rb") as ea_img_file:
            ea_img_file_data: bytes = ea_img_file.read()

        ea_img_memory_file = io.BytesIO(ea_img_file_data)

        for ea_dir in ea_img.dir_entry_list:
            if ea_dir.entry_import_flag:
                ea_img_memory_file.seek(ea_dir.raw_data_offset)
                ea_img_memory_file.write(ea_dir.raw_data)

        out_file_extension: str = get_file_extension(ea_img.f_path)

        logger.info(f"Opening save file dialog for file {ea_img.f_name}...")
        out_file = None
        try:
            out_file = filedialog.asksaveasfile(
                mode="wb",
                defaultextension=out_file_extension,
                initialdir=self.current_save_directory_path,
                initialfile=ea_img.f_name,
                filetypes=(("EA Image File", f"*{out_file_extension}"),),
            )
            try:
                selected_directory = os.path.dirname(out_file.name)
            except Exception:
                selected_directory = ""
            self.current_save_directory_path = selected_directory  # set directory path from history
            self.user_config.set(
                "config", "save_directory_path", selected_directory
            )  # save directory path to config file
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)
        except Exception as error:
            logger.error(f"Error: {error}")
            messagebox.showwarning("Warning", "Failed to save file!")
        if out_file is None:
            return False  # user closed file dialog on purpose

        # Saving data
        ea_img_memory_file.seek(0)
        out_data: Optional[bytes] = ea_img_memory_file.read()
        if not out_data:
            logger.error("Empty data to export!")
            messagebox.showwarning("Warning", "Empty data! Export not possible!")
            return False

        out_file.write(out_data)
        out_file.close()
        messagebox.showinfo("Info", "File saved successfully!")
        logger.info(f"EA Image has been exported successfully to {out_file.name}")
        return True

    def treeview_rclick_open_in_explorer(self, item_iid):
        ea_img = self.tree_view.tree_man.get_object(item_iid, self.opened_ea_images)
        subprocess.Popen(rf'explorer /select,{Path(ea_img.f_path)}"')

    def treeview_rclick_export_image(self, item_iid) -> bool:
        ea_img = self.tree_view.tree_man.get_object(item_iid.split("_")[0], self.opened_ea_images)

        out_data: Optional[bytes] = None
        ea_dir = None
        if "direntry" in item_iid and "binattach" not in item_iid:
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, item_iid)
            if ea_dir.h_record_id not in CONVERT_IMAGES_SUPPORTED_TYPES:
                messagebox.showwarning("Warning", f"Image type {ea_dir.h_record_id} is not supported for export!")
                return False

        else:
            logger.warning("Warning! Unsupported entry while saving output binary data!")

        out_file = None
        try:
            out_file = filedialog.asksaveasfile(
                mode="wb",
                defaultextension=".dds",
                initialdir=self.current_save_directory_path,
                initialfile=ea_img.f_name + "_" + item_iid,
                filetypes=(("DDS files", "*.dds"), ("PNG files", "*.png"), ("BMP files", "*.bmp")),
            )
            try:
                selected_directory = os.path.dirname(out_file.name)
            except Exception:
                selected_directory = ""
            self.current_save_directory_path = selected_directory  # set directory path from history
            self.user_config.set(
                "config", "save_directory_path", selected_directory
            )  # save directory path to config file
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)
        except Exception as error:
            logger.error(f"Error: {error}")
            messagebox.showwarning("Warning", "Failed to save file!")
        if out_file is None:
            return False  # user closed file dialog on purpose

        # pack converted RGBA data
        file_extension: str = get_file_extension_uppercase(out_file.name)
        pillow_wrapper = PillowWrapper()
        out_data = pillow_wrapper.get_pil_image_file_data_for_export(
            ea_dir.img_convert_data, ea_dir.h_width, ea_dir.h_height, pillow_format=file_extension
        )
        del pillow_wrapper
        if not out_data:
            logger.error("Empty data to export!")
            messagebox.showwarning("Warning", "Empty image data! Export not possible!")
            return False

        out_file.write(out_data)
        out_file.close()
        messagebox.showinfo("Info", "File saved successfully!")
        logger.info(f"Image has been exported successfully to {out_file.name}")
        return True

    def treeview_rclick_import_image(self, item_iid) -> bool:
        ea_img = self.tree_view.tree_man.get_object(item_iid.split("_")[0], self.opened_ea_images)

        ea_dir = None
        if "direntry" in item_iid and "binattach" not in item_iid:
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, item_iid)
            if ea_dir.h_record_id not in IMPORT_IMAGES_SUPPORTED_TYPES:
                messagebox.showwarning("Warning", f"Image type {ea_dir.h_record_id} is not supported for IMPORT!")
                return False

        try:
            in_file = filedialog.askopenfile(
                filetypes=self.allowed_import_image_filetypes, mode="rb", initialdir=self.current_open_directory_path
            )
            if not in_file:
                return False
            try:
                selected_directory = os.path.dirname(in_file.name)
            except Exception:
                selected_directory = ""
            self.current_open_directory_path = selected_directory  # set directory path from history
            self.user_config.set(
                "config", "open_directory_path", selected_directory
            )  # save directory path to config file
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)
            in_file_path = in_file.name
        except Exception as error:
            logger.error(f"Failed to open file! Error: {error}")
            messagebox.showwarning("Warning", "Failed to open file!")
            return False

        # import logic (raw data replace)
        pillow_wrapper = PillowWrapper()
        rgba_data: bytes = pillow_wrapper.get_pil_rgba_data_for_import(in_file_path)
        del pillow_wrapper
        import_raw_data: bytes = encode_ea_image(rgba_data, ea_dir)

        if len(import_raw_data) > len(ea_dir.raw_data):
            message: str = "Image data for import is too big. Can't import image!"
            messagebox.showwarning("Warning", message)
            logger.error(message)
            return False

        elif len(import_raw_data) < len(ea_dir.raw_data):
            message: str = "Image data for import is too short. Can't import image!"
            messagebox.showwarning("Warning", message)
            logger.error(message)
            return False

        ea_dir.raw_data = import_raw_data
        ea_dir.entry_import_flag = True

        # preview update logic start
        if len(ea_dir.img_convert_data) != len(rgba_data):
            message: str = "Wrong size of image preview data!"
            messagebox.showwarning("Warning", message)
            logger.error(message)
            return False

        # preview update
        logger.info("Preview update for imported image")
        ea_img.convert_image_data_for_export_and_preview(ea_dir, ea_dir.h_record_id, self)
        self.entry_preview.init_image_preview_logic(ea_dir, item_iid)  # refresh preview for imported image

        # update tree view entry
        checkmark_image = Image.open(self.checkmark_path).resize((15, 15))
        self.checkmark_image = ImageTk.PhotoImage(checkmark_image)
        self.tree_view.treeview_widget.tag_configure(item_iid, font=("Segoe UI", 9, "bold"))
        self.tree_view.treeview_widget.tag_configure(item_iid, image=self.checkmark_image)

        logger.info("Image has been imported successfully")
        return True

    def treeview_rclick_export_raw(self, item_iid):
        ea_img = self.tree_view.tree_man.get_object(item_iid.split("_")[0], self.opened_ea_images)

        out_file = None
        try:
            out_file = filedialog.asksaveasfile(
                mode="wb",
                defaultextension=".bin",
                initialdir=self.current_save_directory_path,
                initialfile=ea_img.f_name + "_" + item_iid,
                filetypes=(("BIN files", "*.bin"), ("all files", "*.*")),
            )
            try:
                selected_directory = os.path.dirname(out_file.name)
            except Exception:
                selected_directory = ""
            self.current_save_directory_path = selected_directory  # set directory path from history
            self.user_config.set(
                "config", "save_directory_path", selected_directory
            )  # save directory path to config file
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)
        except Exception as error:
            logger.error(f"Error: {error}")
            messagebox.showwarning("Warning", "Failed to save file!")
        if out_file is None:
            return

        out_data = None

        if "direntry" in item_iid and "binattach" not in item_iid:
            # get raw image data
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, item_iid)
            out_data = ea_dir.raw_data
        elif "direntry" in item_iid and "binattach" in item_iid:
            # get raw bin attachment data
            dir_iid = item_iid.split("_binattach")[0]
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, dir_iid)
            bin_attach = self.tree_view.tree_man.get_object_bin_attach(ea_dir, item_iid)
            out_data = bin_attach.raw_data
        else:
            logger.warning("Warning! Unsupported entry while saving output binary data!")

        out_file.write(out_data)
        out_file.close()
        messagebox.showinfo("Info", "File saved successfully!")

    def quit_program(self):
        logger.info("Quit GUI...")
        self.master.destroy()

    def open_file(self):
        try:
            in_file = filedialog.askopenfile(
                filetypes=self.allowed_filetypes, mode="rb", initialdir=self.current_open_directory_path
            )
            if not in_file:
                return
            try:
                selected_directory = os.path.dirname(in_file.name)
            except Exception:
                selected_directory = ""
            self.current_open_directory_path = selected_directory  # set directory path from history
            self.user_config.set(
                "config", "open_directory_path", selected_directory
            )  # save directory path to config file
            with open(self.user_config_file_name, "w") as configfile:
                self.user_config.write(configfile)
            in_file_path = in_file.name
            in_file_name = in_file_path.split("/")[-1]
        except Exception as error:
            logger.error(f"Failed to open file! Error: {error}")
            messagebox.showwarning("Warning", "Failed to open file!")
            return

        ea_img = ea_image_main.EAImage()
        sign: bytes = in_file.read(2)
        if sign == b"\x10\xFB":
            in_file.seek(0)
            in_file_data: bytes = in_file.read()
            in_file = io.BytesIO(
                RefpackHandler().decompress_data(in_file_data)
            )  # convert on-disk file to memory file with decompressed data
        in_file.seek(0)
        check_result = ea_img.check_file_signature_and_size(in_file)

        if check_result[0] != "OK":
            error_msg = "ERROR: " + str(check_result[0]) + "\n" + str(check_result[1]) + "\n\n" + "File not supported!"
            messagebox.showwarning("Warning", error_msg)
            return

        logger.info(f"Loading file {in_file_name}...")

        self.ea_image_id += 1
        self.opened_ea_images_count += 1
        ea_img.set_ea_image_id(self.ea_image_id)
        self.opened_ea_images.append(ea_img)

        ea_img.parse_header(in_file, in_file_path, in_file_name)
        ea_img.parse_directory(in_file)

        # check if there are any bin attachments
        # and add them to the list if found
        ea_img.parse_bin_attachments(in_file)

        # convert all supported images
        # in the ea_img file
        try:
            logger.info("Starting processing with convert_images function")
            self.loading_label = tk.Label(self.main_frame, text="Loading... Please wait.", font=("Arial", 14))
            if ea_img.total_f_size > 200000:
                self.loading_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.loading_label.update()
            ea_img.convert_images(self)
            self.loading_label.destroy()
        except Exception as error:
            logger.error(f"Error while converting images! Error: {error}")
            logger.error(traceback.format_exc())

            # set text for header
            if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_sign, ea_img.sign)
                self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_f_size, ea_img.total_f_size)
                self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
                self.set_text_in_box(self.tab_controller.file_header_info_box.fh_text_dir_id, ea_img.format_version)
                self._execute_old_shape_tab_logic()
            elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_sign, ea_img.sign)
                self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_f_size, ea_img.total_f_size)
                self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
                self.set_text_in_box(self.tab_controller.new_shape_file_header_info_box.fh_text_header_and_toc_size, ea_img.header_and_toc_size)
                self._execute_new_shape_tab_logic()

            # set text for the first entry
            if ea_img.sign in OLD_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_rec_type, ea_img.dir_entry_list[0].get_entry_type())
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_size_of_the_block, ea_img.dir_entry_list[0].h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_mipmaps_count, ea_img.dir_entry_list[0].h_mipmaps_count)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_width, ea_img.dir_entry_list[0].h_width)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_height, ea_img.dir_entry_list[0].h_height)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_x, ea_img.dir_entry_list[0].h_center_x)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_center_y, ea_img.dir_entry_list[0].h_center_y)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_left_x, ea_img.dir_entry_list[0].h_default_x_position)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_top_y, ea_img.dir_entry_list[0].h_default_y_position)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_header_offset, ea_img.dir_entry_list[0].h_entry_header_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_offset, ea_img.dir_entry_list[0].raw_data_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_data_size, ea_img.dir_entry_list[0].raw_data_size)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_end_offset, ea_img.dir_entry_list[0].h_entry_end_offset)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_record_id_masked, ea_img.dir_entry_list[0].h_record_id_masked)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_img_compression_masked, ea_img.dir_entry_list[0].h_is_image_compressed_masked)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag1_referenced, ea_img.dir_entry_list[0].h_flag1_referenced)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag2_swizzled, ea_img.dir_entry_list[0].h_flag2_swizzled)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag3_transposed, ea_img.dir_entry_list[0].h_flag3_transposed)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_flag4_reserved, ea_img.dir_entry_list[0].h_flag4_reserved)
                self.set_text_in_box(self.tab_controller.entry_header_info_box.eh_text_entry_image_bpp, ea_img.dir_entry_list[0].h_image_bpp)
                self._execute_old_shape_tab_logic()
            elif ea_img.sign in NEW_SHAPE_ALLOWED_SIGNATURES:
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_rec_type, ea_img.dir_entry_list[0].get_entry_type())
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_size_of_the_block, ea_img.dir_entry_list[0].h_size_of_the_block)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_width, ea_img.dir_entry_list[0].h_width)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_height, ea_img.dir_entry_list[0].h_height)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_left_x, ea_img.dir_entry_list[0].h_default_x_position)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_top_y, ea_img.dir_entry_list[0].h_default_y_position)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_image_bpp, ea_img.dir_entry_list[0].h_image_bpp)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_mipmaps_count, ea_img.dir_entry_list[0].new_shape_number_of_mipmaps)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_int, ea_img.dir_entry_list[0].new_shape_flags)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_flags_hex_str, ea_img.dir_entry_list[0].new_shape_flags_hex_str)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_header_offset, ea_img.dir_entry_list[0].h_entry_header_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_offset, ea_img.dir_entry_list[0].raw_data_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_end_offset, ea_img.dir_entry_list[0].h_entry_end_offset)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_data_size, ea_img.dir_entry_list[0].raw_data_size)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_new_format, ea_img.dir_entry_list[0].new_shape_flag_new_format)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_compressed, ea_img.dir_entry_list[0].new_shape_flag_compressed)
                self.set_text_in_box(self.tab_controller.new_shape_entry_header_info_box.eh_text_entry_flag_swizzled, ea_img.dir_entry_list[0].new_shape_flag_swizzled)
                self._execute_new_shape_tab_logic()


        self.tree_view.tree_man.add_object(ea_img)

        in_file.close()

    def show_about_window(self):
        if not any(isinstance(x, tk.Toplevel) for x in self.master.winfo_children()):
            AboutWindow(self)

    @staticmethod
    def set_text_in_box(in_box, in_text):
        in_box.config(state="normal")
        in_box.delete("1.0", tk.END)
        in_box.insert(tk.END, in_text)
        in_box.config(state="disabled")

    @staticmethod
    def close_toplevel_window(wind):
        wind.destroy()

# fmt: on
