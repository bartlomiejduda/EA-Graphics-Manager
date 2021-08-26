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

VERSION_NUM = "v0.6.16"

import ea_image_logic
import tkinter as tk
import GUI
import center_tk_window    # pip install center_tk_window
import logger


    
def main():
    '''
    Main function of this program.
    '''   
    main_switch = 2
    # 1 - data export test
    # 2 - GUI test
    

    if main_switch == 1:
        p_in_file_path = "E:\\XENTAX\\EA SSH FSH Research\\EA SAMPLES\\NHL 2002 SSH\\awards.ssh"
        p_out_folder_path = "E:\\XENTAX\\EA SSH FSH Research\\EA SAMPLES\\NHL 2002 SSH\\awards.ssh_OUT\\"
              
        ea_image_logic.export_data(p_in_file_path, p_out_folder_path)
        
    elif main_switch == 2:
        #main window
        root = tk.Tk()
        ea_man_gui = GUI.EA_MAN_GUI(root, VERSION_NUM)
        center_tk_window.center_on_screen(root)
        root.mainloop()        
        
    else:
        logger.console_logger("Wrong option selected!")
        
        
    
    logger.console_logger("End of main...")    
    
    
if __name__ == '__main__':   
    main()