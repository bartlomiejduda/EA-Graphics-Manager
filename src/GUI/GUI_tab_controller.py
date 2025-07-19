import tkinter as tk
from tkinter import ttk

from src.GUI.GUI_info_box_entry_header import GuiEntryHeaderInfoBox
from src.GUI.GUI_info_box_file_header import GuiFileHeaderInfoBox
from src.GUI.GUI_info_box_new_shape_entry_header import GuiNewShapeEntryHeaderInfoBox
from src.GUI.GUI_info_box_new_shape_file_header import GuiNewShapeFileHeaderInfoBox


class GuiTabController(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.tab_controller_box = ttk.Notebook(parent)
        self.tab_controller_box.place(x=140, y=5, width=355, height=450)

        self.tab1_old_shape = ttk.Frame(self.tab_controller_box)
        self.tab2_new_shape = ttk.Frame(self.tab_controller_box)

        self.tab_controller_box.add(self.tab1_old_shape, text="Old Shape")
        self.tab_controller_box.add(self.tab2_new_shape, text="New Shape")

        # Old Shape Boxes
        self.file_header_info_box = GuiFileHeaderInfoBox(self.tab1_old_shape, gui_main)
        self.entry_header_info_box = GuiEntryHeaderInfoBox(self.tab1_old_shape, gui_main)

        # New Shape Boxes
        self.new_shape_file_header_info_box = GuiNewShapeFileHeaderInfoBox(self.tab2_new_shape, gui_main)
        self.new_shape_entry_header_info_box = GuiNewShapeEntryHeaderInfoBox(self.tab2_new_shape, gui_main)
