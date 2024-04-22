# -*- coding: utf-8 -*-

"""
Copyright © 2023  Bartłomiej Duda
License: GPL-3.0 License
"""

import os
import tkinter as tk
import webbrowser
from configparser import ConfigParser
from tkinter import filedialog, messagebox

from reversebox.common.logger import get_logger

from src.EA_Image import ea_image_main
from src.EA_Image.constants import PALETTE_TYPES
from src.GUI.about_window import AboutWindow
from src.GUI.GUI_entry_header_info_box import GuiEntryHeaderInfoBox
from src.GUI.GUI_entry_preview import GuiEntryPreview
from src.GUI.GUI_file_header_info_box import GuiFileHeaderInfoBox
from src.GUI.GUI_menu import GuiMenu
from src.GUI.GUI_treeview import GuiTreeView

# default app settings
WINDOW_HEIGHT = 350
WINDOW_WIDTH = 840
MIN_WINDOW_HEIGHT = WINDOW_HEIGHT
MIN_WINDOW_WIDTH = WINDOW_WIDTH
MAX_WINDOW_HEIGHT = WINDOW_HEIGHT
MAX_WINDOW_WIDTH = WINDOW_WIDTH


logger = get_logger(__name__)


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
        self.icon_dir = self.MAIN_DIRECTORY + "\\data\\img\\ea_icon.ico"

        try:
            self.master.iconbitmap(self.icon_dir)
        except tk.TclError:
            logger.error(f"Can't load the icon file from {self.icon_dir}")

        self.allowed_filetypes = [
            (
                "EA Graphics files",
                ["*.fsh", "*.psh", "*.ssh", "*.msh", "*.xsh", "*.gsh"],
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
        self.file_header_info_box = GuiFileHeaderInfoBox(self.main_frame, self)
        self.entry_header_info_box = GuiEntryHeaderInfoBox(self.main_frame, self)
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
    def treeview_widget_select(self, event):
        item_iid = self.tree_view.treeview_widget.identify_row(event.y)

        if item_iid == "":
            return  # quit if nothing is selected

        item_id = item_iid.split("_")[0]

        ea_img = self.tree_view.tree_man.get_object(item_id, self.opened_ea_images)

        # set text for header
        # fmt: off
        self.set_text_in_box(self.file_header_info_box.fh_text_sign, ea_img.sign)
        self.set_text_in_box(self.file_header_info_box.fh_text_f_size, ea_img.total_f_size)
        self.set_text_in_box(self.file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
        self.set_text_in_box(self.file_header_info_box.fh_text_dir_id, ea_img.dir_id)
        # fmt: on

        # set text for dir entry
        if "direntry" in item_iid and "binattach" not in item_iid:
            ea_dir = self.tree_view.tree_man.get_object_dir(ea_img, item_iid)
            # fmt: off
            self.set_text_in_box(self.entry_header_info_box.eh_text_rec_type, ea_dir.get_entry_type())
            self.set_text_in_box(self.entry_header_info_box.eh_text_size_of_the_block, ea_dir.h_size_of_the_block)
            self.set_text_in_box(self.entry_header_info_box.eh_text_mipmaps_count, ea_dir.h_mipmaps_count)
            self.set_text_in_box(self.entry_header_info_box.eh_text_width, ea_dir.h_width)
            self.set_text_in_box(self.entry_header_info_box.eh_text_height, ea_dir.h_height)
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_x, ea_dir.h_center_x)
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_y, ea_dir.h_center_y)
            self.set_text_in_box(self.entry_header_info_box.eh_text_left_x, ea_dir.h_left_x_pos)
            self.set_text_in_box(self.entry_header_info_box.eh_text_top_y, ea_dir.h_top_y_pos)
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_header_offset, ea_dir.h_entry_header_offset)
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_offset, ea_dir.raw_data_offset)
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_size, ea_dir.raw_data_size)
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_end_offset, ea_dir.h_entry_end_offset)
            # fmt: on

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
            # fmt: off
            self.set_text_in_box(self.entry_header_info_box.eh_text_rec_type, bin_attach.get_entry_type())
            self.set_text_in_box(self.entry_header_info_box.eh_text_size_of_the_block, bin_attach.h_size_of_the_block)
            self.set_text_in_box(self.entry_header_info_box.eh_text_mipmaps_count, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_width, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_height, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_x, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_y, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_left_x, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_top_y, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_header_offset, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_offset, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_size, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_end_offset, "")
            # fmt: on

            # bin attachment preview logic START
            try:
                self.entry_preview.preview_instance.destroy()
            except Exception:
                pass

            # fmt: off
            if bin_attach.h_record_id in PALETTE_TYPES:  # palette types
                self.entry_preview.init_palette_preview_logic(bin_attach)
            else:
                self.entry_preview.init_binary_preview_logic(bin_attach)
            # fmt: on
            # bin attachment preview logic END

        else:
            # fmt: off
            self.set_text_in_box(self.entry_header_info_box.eh_text_rec_type, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_size_of_the_block, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_mipmaps_count, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_width, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_height, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_x, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_center_y, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_left_x, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_top_y, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_header_offset, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_offset, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_data_size, "")
            self.set_text_in_box(self.entry_header_info_box.eh_text_entry_end_offset, "")
            # fmt: on

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
            self.tree_rclick_popup.add_command(label="Close File", command=lambda: self.treeview_rclick_close(item_iid))
            self.tree_rclick_popup.tk_popup(event.x_root, event.y_root, entry="0")
        elif "direntry" in item_iid and "binattach" not in item_iid:
            self.tree_rclick_popup.add_command(
                label="Export Raw Image Data",
                command=lambda: self.treeview_rclick_export_raw(item_iid),
            )
            # self.tree_rclick_popup.add_command(label="Export Image As BMP")
            # self.tree_rclick_popup.add_command(label="Export Image Details As XML")
            # self.tree_rclick_popup.add_command(label="Import Raw Image Data")
            # self.tree_rclick_popup.add_command(label="Import Image From BMP")
            # self.tree_rclick_popup.add_command(label="Import Image Details From XML")
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
        del ea_img  # removing object from memory

        self.set_text_in_box(self.file_header_info_box.fh_text_sign, "")
        self.set_text_in_box(self.file_header_info_box.fh_text_f_size, "")
        self.set_text_in_box(self.file_header_info_box.fh_text_obj_count, "")
        self.set_text_in_box(self.file_header_info_box.fh_text_dir_id, "")

    def treeview_rclick_export_raw(self, item_iid):
        ea_img = self.tree_view.tree_man.get_object(item_iid.split("_")[0], self.opened_ea_images)

        out_file = None
        try:
            out_file = filedialog.asksaveasfile(
                mode="wb+",
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
            ea_img.convert_images()
            self.loading_label.destroy()
        except Exception as error:
            logger.error(f"Error while converting images! Error: {error}")

        # fmt: off
        # set text for header
        self.set_text_in_box(self.file_header_info_box.fh_text_sign, ea_img.sign)
        self.set_text_in_box(self.file_header_info_box.fh_text_f_size, ea_img.total_f_size)
        self.set_text_in_box(self.file_header_info_box.fh_text_obj_count, ea_img.num_of_entries)
        self.set_text_in_box(self.file_header_info_box.fh_text_dir_id, ea_img.dir_id)

        # set text for the first entry
        self.set_text_in_box(self.entry_header_info_box.eh_text_rec_type, ea_img.dir_entry_list[0].get_entry_type())
        self.set_text_in_box(self.entry_header_info_box.eh_text_size_of_the_block, ea_img.dir_entry_list[0].h_size_of_the_block)
        self.set_text_in_box(self.entry_header_info_box.eh_text_mipmaps_count, ea_img.dir_entry_list[0].h_mipmaps_count)
        self.set_text_in_box(self.entry_header_info_box.eh_text_width, ea_img.dir_entry_list[0].h_width)
        self.set_text_in_box(self.entry_header_info_box.eh_text_height, ea_img.dir_entry_list[0].h_height)
        self.set_text_in_box(self.entry_header_info_box.eh_text_center_x, ea_img.dir_entry_list[0].h_center_x)
        self.set_text_in_box(self.entry_header_info_box.eh_text_center_y, ea_img.dir_entry_list[0].h_center_y)
        self.set_text_in_box(self.entry_header_info_box.eh_text_left_x, ea_img.dir_entry_list[0].h_left_x_pos)
        self.set_text_in_box(self.entry_header_info_box.eh_text_top_y, ea_img.dir_entry_list[0].h_top_y_pos)
        self.set_text_in_box(self.entry_header_info_box.eh_text_entry_header_offset, ea_img.dir_entry_list[0].h_entry_header_offset)
        self.set_text_in_box(self.entry_header_info_box.eh_text_data_offset, ea_img.dir_entry_list[0].raw_data_offset)
        self.set_text_in_box(self.entry_header_info_box.eh_text_data_size, ea_img.dir_entry_list[0].raw_data_size)
        self.set_text_in_box(self.entry_header_info_box.eh_text_entry_end_offset, ea_img.dir_entry_list[0].h_entry_end_offset)
        # fmt: on

        self.tree_view.tree_man.add_object(ea_img)

        in_file.close()

    def show_about_window(self):
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

    @staticmethod
    def web_callback(url):
        webbrowser.open_new(url)
