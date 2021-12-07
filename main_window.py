"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import argparse
import json
import tkinter as tk
import os

from dev_common import get_dummy_dict, get_empty_dict, recurse_hover, recurse_tk_structure

# when called by RPC the directory may change and be unable to find the ttk theme file directory
from popup_frame import PopupFrame

os.chdir(r'C:\Users\lmcglaughlin\PycharmProjects\mahlo_popup')


class Popup(tk.Tk):
    def __init__(self, input_dict, *args, **kwargs):
        super().__init__()
        self.debugging = kwargs.get('debug')
        self.attributes('-toolwindow', True)

        # styling
        self.tk.call("source", "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl")
        self.tk.call("set_theme", "dark")
        # frame padding
        self.pad = dict(
            x=5,
            y=3
        )
        self._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': 'Card.TFrame'}

        params = {'style_settings': {'pad': self.pad, '_wgt_styles': self._wgt_styles}}

        self.popup_frame = PopupFrame(self, input_dict, **params)
        self.popup_frame.grid(row=0, column=0, sticky='nesw')

        # move the window to the front
        self.lift()
        self.attributes('-topmost', True)
        # self.root.after_idle(self.root.attributes, '-topmost', False)

        # shrink to a button when not the focus window
        self.bind("<FocusOut>", self.popup_frame.focus_lost_handler)

        self.bind("<FocusIn>", self.popup_frame.focus_gained_handler)

        self.columnconfigure(0, weight=1)  # to make the button able to fill the width
        self.rowconfigure(0, weight=1)  # to make the button able to fill the height

        if self.debugging:
            def recursive_print():
                recurse_tk_structure(self)
                self.after(15000, recursive_print)

            self.after(1000, recursive_print)  # for debugging, prints out the tkinter structure
            recurse_hover(self.popup_frame)  # for debugging, shows widget info when mouse cursor moves over it

        self.mainloop()


# TODO:
#  need to talk to some operators about how long until it makes sense to popup
#  doing it too soon they wouldn't have a chance and could be disruptive
#  respond (send it to a database?)
#  check that this will work over ssl (opening in the normal session) otherwise probably flask


def dev_popup(json_str=None):
    # for development, a dummy dict
    if json_str is None:
        oospec_len_meters = 4.3
        test_json_dict = get_dummy_dict(oospec_len_meters)
        json_str = json.dumps(test_json_dict)
    pup_dict = json.loads(json_str)
    pup = Popup(pup_dict)


def dev_popup_empty(json_str=None):
    # for development, a dummy dict
    if json_str is None:
        oospec_len_meters = 4.3
        test_json_dict = get_empty_dict()
        json_str = json.dumps(test_json_dict)
    pup_dict = json.loads(json_str)
    pup = Popup(pup_dict)


if __name__ == '__main__':
    # if called from the command line (over ssl) parse the json to a dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument('--pup_json', help='A json string defining the popups to display.')
    args = parser.parse_args()
    json_str = args.pup_json

    dev_popup()
    dev_popup_empty()
