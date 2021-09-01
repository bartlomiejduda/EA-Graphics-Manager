# -*- coding: utf-8 -*-

'''
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License 
'''


# Program tested on Python 3.7.0

# Ver      Date        Author               Comment
# v0.1     23.01.2021  Bartlomiej Duda      -
# v0.2     28.01.2021  Bartlomiej Duda      -
# v0.3     30.01.2021  Bartlomiej Duda      -
# v0.4     31.01.2021  Bartlomiej Duda      Added BMP class
# v0.5     02.02.2021  Bartlomiej Duda      New image types partially reverse engineered
# v0.6     10.08.2021  Bartlomiej Duda      Added new modules, moved to new repository
# v0.6.2   13.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.3   13.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.4   14.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.5   14.08.2021  Bartlomiej Duda      Enhanced GUI (file opening, header info), added EA_IMAGE class
# v0.6.6   14.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.7   15.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.8   17.08.2021  Bartlomiej Duda      Enhanced GUI (added entry header info)
# v0.6.9   18.08.2021  Bartlomiej Duda      Enhanced GUI
# v0.6.10  19.08.2021  Bartlomiej Duda      Enhanced GUI, added "logger" file
# v0.6.11  19.08.2021  Bartlomiej Duda      Enhanced GUI, added "make_exe" script 
# v0.6.12  20.08.2021  Bartlomiej Duda      Enhanced "make_exe" script
# v0.6.13  20.08.2021  Bartlomiej Duda      Enhanced GUI (better treeview logic)
# v0.6.14  20.08.2021  Bartlomiej Duda      Enhanced ea_image_logic
# v0.6.15  25.08.2021  Bartlomiej Duda      Enhanced ea_image_logic & GUI
# v0.6.16  26.08.2021  Bartlomiej Duda      Enhanced ea_image_logic & GUI
# v0.6.17  28.08.2021  Bartlomiej Duda      Enhanced ea_image_logic & GUI
# v0.7.0   28.08.2021  Bartlomiej Duda      Added stub for console mode, Enhanced ea_image_logic & GUI
# v0.7.1   29.08.2021  Bartlomiej Duda      Enhanced ea_image_logic (added parsing for binary attachments), Enhanced GUI
# v0.7.2   01.09.2021  Bartlomiej Duda      Enhanced ea_image_logic & GUI (added exporting raw data)

VERSION_NUM = "v0.7.2"

import ea_image_logic
import tkinter as tk
import GUI
import center_tk_window  # pip install center_tk_window
import logger
import argparse


def main():
    '''
    Main function of this program.
    If you want to work in console mode, you have to specify correct arguments.
    GUI mode is the default one. No arguments are required if you want to work in GUI mode.
    '''   

    
    parser = argparse.ArgumentParser(description='Program to parse EA graphics files.')
    parser.add_argument('-d', '--dir', metavar='', help='Extract images from all files in specified directory')
    parser.add_argument('-e', '--extract', metavar='', help='Extract images from specified file')
    parser.add_argument('-o', '--out', metavar='', help='Output directory')
    args = parser.parse_args()    
    
    if (args.dir is not None and args.extract is not None):
        logger.console_logger("You can't use \"dir\" and \"extract\" arguments at the same time. Exiting...")   
        return
    
    elif (args.dir is not None and args.out is not None):
        logger.console_logger("Extracting from specified directory...")
        # TODO 
        
    elif (args.extract is not None and args.out is not None):
        logger.console_logger("Extracting from specified file...")
        # TODO
        
    elif (args.dir is None and args.extract is None and args.out is None):
        #GUI mode
        root = tk.Tk()
        ea_man_gui = GUI.EA_MAN_GUI(root, VERSION_NUM)
        center_tk_window.center_on_screen(root)
        root.mainloop()        
        
    else:
        logger.console_logger("Invalid arguments! Exiting...")
        
    
    logger.console_logger("End of main...")    
    
    
if __name__ == '__main__':   
    main()