import math
import tkinter as tk

from PIL import Image, ImageTk
from reversebox.common.logger import get_logger

from src.EA_Image.bin_attachment_entries import PaletteEntry

logger = get_logger(__name__)


# fmt: off

class GuiEntryPreview(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.preview_labelframe_width = 440
        self.preview_labelframe_height = 450
        self.canvas_height = self.preview_labelframe_height - 30
        self.canvas_width = self.preview_labelframe_width - 20
        self.preview_labelframe = tk.LabelFrame(parent, text="Preview")
        self.preview_labelframe.place(x=500, y=5, width=self.preview_labelframe_width, height=self.preview_labelframe_height)

        self.ph_img = None
        self.preview_instance = None

    def init_image_preview_logic(self, ea_dir, item_iid):
        if not ea_dir.img_convert_data or len(ea_dir.img_convert_data) == 0:
            logger.error(f"Preview failed for {str(item_iid)}, because converted image data is empty!")
            return

        try:
            pil_img = Image.frombuffer(
                "RGBA",
                (int(ea_dir.h_width), int(ea_dir.h_height)),
                ea_dir.img_convert_data,
                "raw",
                "RGBA",
                0,
                1,
            )

            # resize preview logic
            if pil_img.height >= pil_img.width:
                if pil_img.height > self.canvas_height:
                    ratio: float = self.canvas_height / pil_img.height
                    resized_height: int = int(pil_img.height * ratio)
                    resized_width: int = int(pil_img.width * ratio)
                    pil_img = pil_img.resize((resized_width, resized_height))
            else:
                if pil_img.width > self.canvas_width:
                    ratio: float = self.canvas_width / pil_img.width
                    resized_height: int = int(pil_img.height * ratio)
                    resized_width: int = int(pil_img.width * ratio)
                    pil_img = pil_img.resize((resized_width, resized_height))

            self.ph_img = ImageTk.PhotoImage(pil_img)

            self.preview_instance = tk.Canvas(
                self.preview_labelframe,
                bg="#595959",
                width=self.canvas_width,
                height=self.canvas_height,
            )
            self.preview_instance.create_image(
                int(self.canvas_width / 2),
                int(self.canvas_height / 2),
                anchor="center",
                image=self.ph_img,
            )
            self.preview_instance.place(x=5, y=5)

        except Exception as error:
            logger.error(f"Error occurred while generating preview for {str(item_iid)}... Error: {error}")

    def init_image_preview_not_supported_logic(self):
        preview_text = "Preview for this image type is not supported..."
        self.preview_instance = tk.Label(
            self.preview_labelframe,
            text=preview_text,
            anchor="nw",
            justify="left",
            wraplength=300,
        )
        self.preview_instance.place(x=5, y=5, width=285, height=130)

    def init_binary_preview_logic(self, bin_attachment):
        preview_hex_string = bin_attachment.raw_data.decode("utf8", "backslashreplace").replace("\000", ".")[
            0:200
        ]  # limit preview to 200 characters
        self.preview_instance = tk.Label(
            self.preview_labelframe,
            text=preview_hex_string,
            anchor="nw",
            justify="left",
            wraplength=300,
        )
        self.preview_instance.place(x=5, y=5, width=285, height=130)

    def init_palette_preview_logic(self, palette_entry: PaletteEntry):
        palette_width: int = palette_entry.pal_width
        palette_height: int = palette_entry.pal_height

        try:
            pil_img = Image.frombuffer(
                "RGBA",
                (math.ceil(palette_width / 2), math.ceil(palette_height / 2)),
                palette_entry.raw_data,
                "raw",
                "RGBA",
                0,
                1,
            )

            if pil_img.height > self.canvas_height:
                ratio = self.canvas_height / pil_img.height
                pil_img = pil_img.resize((int(pil_img.width * ratio), self.canvas_height))
            elif pil_img.height < 50:
                pil_img = pil_img.resize((int(pil_img.width * 6), int(pil_img.height * 6)))

            self.ph_img = ImageTk.PhotoImage(pil_img)

            self.preview_instance = tk.Canvas(
                self.preview_labelframe,
                bg="#595959",
                width=self.canvas_width,
                height=self.canvas_height,
            )
            self.preview_instance.create_image(
                self.canvas_width / 2,
                self.canvas_height / 2,
                anchor="center",
                image=self.ph_img,
            )
            self.preview_instance.place(x=5, y=5)

        except Exception as error:
            logger.error(f"Error occurred while generating preview palette... Error: {error}")
