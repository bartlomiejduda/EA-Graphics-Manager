# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License
"""

import tkinter as tk
import GUI
import center_tk_window
import logger
import argparse

# Program tested on Python 3.7.0


VERSION_NUM = "v0.10.0"


def main():
    """
    Main function of this program.
    If you want to work in console mode, you have to specify correct arguments.
    GUI mode is the default one. No arguments are required if you want to work in GUI mode.
    """

    parser = argparse.ArgumentParser(description="Program to parse EA graphics files.")
    parser.add_argument(
        "-d",
        "--dir",
        metavar="",
        help="Extract images from all files in specified directory",
    )
    parser.add_argument(
        "-e", "--extract", metavar="", help="Extract images from specified file"
    )
    parser.add_argument("-o", "--out", metavar="", help="Output directory")
    args = parser.parse_args()

    if args.dir is not None and args.extract is not None:
        logger.console_logger(
            'You can\'t use "dir" and "extract" arguments at the same time. Exiting...'
        )
        return

    elif args.dir is not None and args.out is not None:
        logger.console_logger("Extracting from specified directory...")
        # TODO

    elif args.extract is not None and args.out is not None:
        logger.console_logger("Extracting from specified file...")
        # TODO

    elif args.dir is None and args.extract is None and args.out is None:
        # GUI mode
        root = tk.Tk()
        GUI.EAManGui(root, VERSION_NUM)  # start GUI
        root.lift()
        center_tk_window.center_on_screen(root)
        root.mainloop()

    else:
        logger.console_logger("Invalid arguments! Exiting...")

    logger.console_logger("End of main...")


if __name__ == "__main__":
    main()
