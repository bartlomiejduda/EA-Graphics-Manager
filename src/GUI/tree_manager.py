import tkinter as tk

from reversebox.common.logger import get_logger

logger = get_logger(__name__)


class TreeManager:
    def __init__(self, in_widget):
        self.tree_widget = in_widget

    def add_object(self, in_obj):
        self.tree_widget.insert(
            "", tk.END, text=in_obj.f_name, iid=in_obj.ea_image_id, open=True
        )  # add file to tree, eg. "awards.ssh"

        # add object children (ea images) to tree
        sub_id = 0
        for dir_entry in in_obj.dir_entry_list:
            sub_id += 1
            self.tree_widget.insert(
                "", tk.END, text=dir_entry.tag, iid=dir_entry.id, open=False
            )
            self.tree_widget.move(dir_entry.id, in_obj.ea_image_id, sub_id)

            # add binary attachments to tree
            bin_att_sub_id = 0
            for bin_att_entry in dir_entry.bin_attachments_list:
                bin_att_sub_id += 1
                self.tree_widget.insert(
                    "",
                    tk.END,
                    text=bin_att_entry.tag,
                    iid=bin_att_entry.id,
                    open=True,
                )
                self.tree_widget.move(bin_att_entry.id, dir_entry.id, bin_att_sub_id)

    @staticmethod
    def get_object(in_id, in_ea_images):
        for ea_img in in_ea_images:
            if int(in_id) == int(ea_img.ea_image_id):
                return ea_img

        logger.warning("Warning! Couldn't find matching ea_img object!")
        return None

    @staticmethod
    def get_object_dir(in_ea_img, in_iid):
        for ea_dir in in_ea_img.dir_entry_list:
            if in_iid == ea_dir.id:
                return ea_dir

        logger.warning("Warning! Couldn't find matching DIR object!")
        return None

    @staticmethod
    def get_object_bin_attach(in_dir_entry, in_iid):
        for bin_attach in in_dir_entry.bin_attachments_list:
            if in_iid == bin_attach.id:
                return bin_attach

        logger.warning("Warning! Couldn't find matching BIN_ATTACHMENT object!")
        return None
