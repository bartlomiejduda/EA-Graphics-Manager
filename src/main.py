"""
Copyright © 2024-2025  Bartłomiej Duda
License: GPL-3.0 License
"""

# Program tested on Python 3.11.6

import os
import tkinter as tk

import center_tk_window
from reversebox.common.logger import get_logger

from src.GUI.GUI_main import EAManGui

VERSION_NUM = "v0.35.3"

logger = get_logger("main")

MAIN_DIRECTORY = os.getcwd()


def main():
    """
    Main function of this program.
    It will run EA Graphics Manager in GUI mode.
    """

    logger.info("Starting main...")

    root = tk.Tk()
    EAManGui(root, VERSION_NUM, MAIN_DIRECTORY)  # start GUI
    root.lift()
    center_tk_window.center_on_screen(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

    logger.info("End of main...")


if __name__ == "__main__":
    main()
