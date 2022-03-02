# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License
"""

# Program tested on Python 3.7.0


import tkinter as tk
import GUI
import center_tk_window
from logger import get_logger


VERSION_NUM = "v0.10.2"

logger = get_logger("main")


def main():
    """
    Main function of this program.
    If you want to work in console mode, you have to specify correct arguments.
    GUI mode is the default one. No arguments are required if you want to work in GUI mode.
    """

    logger.info("Starting main...")

    root = tk.Tk()
    GUI.EAManGui(root, VERSION_NUM)  # start GUI
    root.lift()
    center_tk_window.center_on_screen(root)
    root.mainloop()

    logger.info("End of main...")


if __name__ == "__main__":
    main()
