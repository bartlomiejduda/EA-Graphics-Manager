import tkinter as tk

from src.GUI.right_clicker import RightClicker


class GuiEntryHeaderInfoBox(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.entry_header_labelframe = tk.LabelFrame(parent, text="Entry Header")
        self.entry_header_labelframe.place(x=140, y=100, width=340, height=320)  # <-- entry header info box

        # Record ID
        self.eh_label_rec_type = tk.Label(self.entry_header_labelframe, text="Record ID:", anchor="w")
        self.eh_label_rec_type.place(x=5, y=5, width=80, height=20)  # <-- record type label
        self.eh_text_rec_type = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_rec_type.place(x=70, y=5, width=260, height=20)  # <-- record type box
        self.eh_text_rec_type.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Size Of The Block
        self.eh_label_size_of_the_block = tk.Label(self.entry_header_labelframe, text="Size Of The Block:", anchor="w")
        self.eh_label_size_of_the_block.place(x=5, y=35, width=120, height=20)  # <-- size of the block label
        self.eh_text_size_of_the_block = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_size_of_the_block.place(x=110, y=35, width=90, height=20)  # <-- size of the block box
        self.eh_text_size_of_the_block.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Number Of Mipmaps
        self.eh_label_mipmaps_count = tk.Label(self.entry_header_labelframe, text="Mipmaps:", anchor="w")
        self.eh_label_mipmaps_count.place(x=215, y=35, width=70, height=20)  # <-- mipmaps label
        self.eh_text_mipmaps_count = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_mipmaps_count.place(x=280, y=35, width=50, height=20)  # <-- mipmaps box
        self.eh_text_mipmaps_count.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image Width
        self.eh_label_width = tk.Label(self.entry_header_labelframe, text="Width:", anchor="w")
        self.eh_label_width.place(x=5, y=65, width=80, height=20)
        self.eh_text_width = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_width.place(x=70, y=65, width=60, height=20)
        self.eh_text_width.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image Height
        self.eh_label_height = tk.Label(self.entry_header_labelframe, text="Height:", anchor="w")
        self.eh_label_height.place(x=140, y=65, width=80, height=20)
        self.eh_text_height = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_height.place(x=200, y=65, width=60, height=20)
        self.eh_text_height.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Center X
        self.eh_label_center_x = tk.Label(self.entry_header_labelframe, text="Center X:", anchor="w")
        self.eh_label_center_x.place(x=5, y=95, width=80, height=20)
        self.eh_text_center_x = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_center_x.place(x=70, y=95, width=60, height=20)
        self.eh_text_center_x.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Center Y
        self.eh_label_center_y = tk.Label(self.entry_header_labelframe, text="Center Y:", anchor="w")
        self.eh_label_center_y.place(x=140, y=95, width=80, height=20)
        self.eh_text_center_y = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_center_y.place(x=200, y=95, width=60, height=20)
        self.eh_text_center_y.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Default Y Position
        self.eh_label_left_x = tk.Label(self.entry_header_labelframe, text="Def X:", anchor="w")
        self.eh_label_left_x.place(x=5, y=125, width=80, height=20)
        self.eh_text_left_x = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_left_x.place(x=70, y=125, width=60, height=20)
        self.eh_text_left_x.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Default Y Position
        self.eh_label_top_y = tk.Label(self.entry_header_labelframe, text="Def Y:", anchor="w")
        self.eh_label_top_y.place(x=140, y=125, width=80, height=20)
        self.eh_text_top_y = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_top_y.place(x=200, y=125, width=60, height=20)
        self.eh_text_top_y.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Entry Header Offset
        self.eh_label_entry_header_offset = tk.Label(self.entry_header_labelframe, text="EH Offset:", anchor="w")
        self.eh_label_entry_header_offset.place(x=5, y=155, width=80, height=20)
        self.eh_text_entry_header_offset = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_header_offset.place(x=70, y=155, width=90, height=20)
        self.eh_text_entry_header_offset.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image Offset
        self.eh_label_data_offset = tk.Label(self.entry_header_labelframe, text="IMG Offset:", anchor="w")
        self.eh_label_data_offset.place(x=170, y=155, width=80, height=20)
        self.eh_text_data_offset = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_data_offset.place(x=240, y=155, width=90, height=20)
        self.eh_text_data_offset.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image End
        self.eh_label_entry_end_offset = tk.Label(self.entry_header_labelframe, text="IMG End:", anchor="w")
        self.eh_label_entry_end_offset.place(x=5, y=185, width=80, height=20)
        self.eh_text_entry_end_offset = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_end_offset.place(x=70, y=185, width=90, height=20)
        self.eh_text_entry_end_offset.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image Size
        self.eh_label_data_size = tk.Label(self.entry_header_labelframe, text="IMG Size:", anchor="w")
        self.eh_label_data_size.place(x=170, y=185, width=80, height=20)
        self.eh_text_data_size = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_data_size.place(x=240, y=185, width=90, height=20)
        self.eh_text_data_size.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Record ID (Masked)
        self.eh_label_record_id_masked = tk.Label(self.entry_header_labelframe, text="Record ID (Masked):", anchor="w")
        self.eh_label_record_id_masked.place(x=5, y=215, width=120, height=20)
        self.eh_text_entry_record_id_masked = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_record_id_masked.place(x=120, y=215, width=50, height=20)
        self.eh_text_entry_record_id_masked.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image Compression
        self.eh_label_img_compression_masked = tk.Label(self.entry_header_labelframe, text="IMG compr.:", anchor="w")
        self.eh_label_img_compression_masked.place(x=180, y=215, width=120, height=20)
        self.eh_text_entry_img_compression_masked = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_img_compression_masked.place(x=260, y=215, width=70, height=20)
        self.eh_text_entry_img_compression_masked.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Flag 1 - Referenced
        self.eh_label_flag1_referenced = tk.Label(self.entry_header_labelframe, text="Flag Ref:", anchor="w")
        self.eh_label_flag1_referenced.place(x=5, y=245, width=120, height=20)
        self.eh_text_entry_flag1_referenced = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_flag1_referenced.place(x=60, y=245, width=30, height=20)
        self.eh_text_entry_flag1_referenced.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Flag 2 - Swizzled
        self.eh_label_flag2_swizzled = tk.Label(self.entry_header_labelframe, text="Flag Swiz:", anchor="w")
        self.eh_label_flag2_swizzled.place(x=100, y=245, width=120, height=20)
        self.eh_text_entry_flag2_swizzled = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_flag2_swizzled.place(x=160, y=245, width=30, height=20)
        self.eh_text_entry_flag2_swizzled.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Flag 3 - Transposed
        self.eh_label_flag3_transposed = tk.Label(self.entry_header_labelframe, text="Flag Trans:", anchor="w")
        self.eh_label_flag3_transposed.place(x=200, y=245, width=120, height=20)
        self.eh_text_entry_flag3_transposed = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_flag3_transposed.place(x=270, y=245, width=30, height=20)
        self.eh_text_entry_flag3_transposed.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Flag 4 - Reserved
        self.eh_label_flag4_reserved = tk.Label(self.entry_header_labelframe, text="Flag Res:", anchor="w")
        self.eh_label_flag4_reserved.place(x=5, y=275, width=120, height=20)
        self.eh_text_entry_flag4_reserved = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_flag4_reserved.place(x=60, y=275, width=30, height=20)
        self.eh_text_entry_flag4_reserved.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))

        # Image BPP
        self.eh_label_image_bpp = tk.Label(self.entry_header_labelframe, text="Image bpp:", anchor="w")
        self.eh_label_image_bpp.place(x=100, y=275, width=120, height=20)
        self.eh_text_entry_image_bpp = tk.Text(
            self.entry_header_labelframe,
            bg=self.entry_header_labelframe["bg"],
            state="disabled",
        )
        self.eh_text_entry_image_bpp.place(x=170, y=275, width=30, height=20)
        self.eh_text_entry_image_bpp.bind("<Button-3>", lambda event, arg=self: RightClicker(arg, event))
