import io
import math

from PIL import ImageTk, Image
import tkinter as tk

from src.EA_Image.Bmp import BmpImg
from src.EA_Image.bin_attachment_entries import PaletteEntry
from src.logger import get_logger

logger = get_logger(__name__)


class GuiEntryPreview(tk.Frame):
    def __init__(self, parent, gui_main):
        super().__init__(parent)

        self.preview_labelframe_width = 340
        self.preview_labelframe_height = 335
        self.canvas_height = self.preview_labelframe_height - 30
        self.canvas_width = self.preview_labelframe_width - 20
        self.preview_labelframe = tk.LabelFrame(parent, text="Preview")
        self.preview_labelframe.place(
            x=490,
            y=5,
            width=self.preview_labelframe_width,
            height=self.preview_labelframe_height,
        )

        self.ph_img = None
        self.preview_instance = None

    def init_image_preview_logic(self, ea_dir, item_iid):
        try:
            pil_img = Image.frombuffer("RGBA", (ea_dir.h_height, ea_dir.h_width), ea_dir.img_convert_data, "raw", "RGBA", 0, 1)

            if pil_img.height > self.canvas_height:
                ratio = self.canvas_height / pil_img.height
                pil_img = pil_img.resize(
                    (int(pil_img.width * ratio), self.canvas_height)
                )

            self.ph_img = ImageTk.PhotoImage(pil_img)

            self.preview_instance = tk.Canvas(
                self.preview_labelframe,
                bg="white",
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
            logger.error(
                "Error occurred while generating preview for %s... Error: %s",
                str(item_iid),
                error,
            )

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
        preview_hex_string = bin_attachment.raw_data.decode(
            "utf8", "backslashreplace"
        ).replace("\000", ".")[
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
        # TODO - move this logic (before "try") to EAImage
        # TODO - fix palette - RGB to BGR
        bytes_per_entry_in_palette: int = int(len(palette_entry.raw_data) / palette_entry.pal_entries)
        palette_width: int = int(math.sqrt(palette_entry.pal_entries))
        palette_height: int = int(math.sqrt(palette_entry.pal_entries))
        bmp_object = BmpImg(
            palette_width, palette_height, bytes_per_entry_in_palette, palette_entry.raw_data, b"")

        try:
            img_file_stream = io.BytesIO(bmp_object.get_bmp_file_data())
            pil_img = Image.open(img_file_stream).transpose(Image.FLIP_TOP_BOTTOM)

            if pil_img.height > self.canvas_height:
                ratio = self.canvas_height / pil_img.height
                pil_img = pil_img.resize(
                    (int(pil_img.width * ratio), self.canvas_height)
                )
            elif pil_img.height < 50:
                pil_img = pil_img.resize((int(pil_img.width * 6), int(pil_img.height * 6)))

            self.ph_img = ImageTk.PhotoImage(pil_img)

            self.preview_instance = tk.Canvas(
                self.preview_labelframe,
                bg="white",
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
            logger.error(
                "Error occurred while generating preview palette... Error: %s",
                error,
            )
