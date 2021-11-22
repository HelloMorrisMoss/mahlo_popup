"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import argparse
import json
import tkinter as tk
import traceback
from tkinter import ttk
from datetime import datetime
import os
from pprint import pprint  # for dev
import logging

from msg_panel import MessagePanel

# init the logger
lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)
# when called by RPC the directory may change and be unable to find the ttk theme file directory
os.chdir(r'C:\Users\lmcglaughlin\PycharmProjects\mahlo_popup')


class Popup:
    """A popup window with messages to respond to. Create the window and messages based on a provided dictionary.

    """

    def __init__(self, input_dict, *args, **kwargs):
        """
        example_input_dict = {'messages': [{'title': 'Out of spec!',
                                        'msg_txt': {'template': template_str,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'length_in_meters': oospec_len_meters},
                                        'buttons': ['removed!', 'oops!'],
                                        'msg_id': msg_id
                                        }
                                       for msg_id in ('msg123', 'msg456', 'msg789')],
                          'main_win': {'title': 'Messages received!'}
                          }
            messages: a list of message dictionaries. Each of which should include:
               title: a string title for the message frame
            main_win: a dictionary of parameters for the window apart from the messages.
                title: a string with the title for the main window.
        :param input_dict:
        """
        # pprint(json.dumps(input_dict, indent=4))
        pprint(input_dict)
        # set things up for the main window
        self._defdic = input_dict
        self.root = tk.Tk()
        self.root.title(self._defdic['main_win']['title'])
        # self.root.geometry('1000x500')
        self.wgts = {}
        self.styling()

        self._removed_state_vars = {
            msg['msg_id']: {'all': tk.IntVar(), 'left': tk.IntVar(), 'left_center': tk.IntVar(), 'center': tk.IntVar(), 'right_center': tk.IntVar(), 'right': tk.IntVar()}
            for msg in self._defdic['messages']}
        for mid, state_dict in self._removed_state_vars.items():
            state_dict['all'].set(True)

        # the format for the datetime strftime to use for display
        self.dt_format_str = self._defdic['main_win']['timestamp_display_format']

        # the main frame
        self.main_frm = tk.ttk.Frame(self.root)
        self.main_frm.grid(row=1, column=0, sticky='nesw', columnspan=3)
        # dummy = ttk.Checkbutton(self.main_frm, text='dummy button')
        # dummy.grid(row=0, column=0)

        # self.wigify(self.main_frm)
        # # me.hover_enter_factory(me.main_frm)
        self.wgts['main_frame'] = self.main_frm

        self.messages_frames = []

        # add the frames for the messages and the widgets therein
        for mnum, message in enumerate(self._defdic['messages']):
            msg_frm = MessagePanel(self.main_frm, self.root, message, mnum, dt_format_str=self.dt_format_str, pad={'x': self.pad['x'], 'y': self.pad['y']},
                         _wgt_styles=self._wgt_styles)
            self.messages_frames.append(msg_frm)

        # me.recurse_hover(me.wgts)
        self.recurse_tk_structure(self.root)

        # move the window to the front
        self.root.lift()
        # self.root.attributes('-topmost', True)
        # self.root.after_idle(self.root.attributes, '-topmost', False)

        # shrink to a button when not the focus window
        self.root.bind("<FocusOut>", self.focus_lost_handler)
        self.root.bind("<FocusIn>", self.focus_gained_handler)

        self.root.mainloop()

    def focus_gained_handler(self, event):
        """When the window gains focus.

        :param event: tkinter.Event
        """
        lg.debug(event.widget == self.root)
        if event.widget == self.root:
            lg.debug('Focus window!')
            for mf in self.messages_frames:
                mf.un_hide()
            self.main_frm.grid()

    def focus_lost_handler(self, event):
        """When the window loses focus (another window is clicked or otherwise switched to).

        :param event: tkinter.Event
        """
        lg.debug(event.widget == self.root)
        if event.widget == self.root:
            lg.debug('No longer focus window!')
            for mf in self.messages_frames:
                mf.hide()
            # self.main_frm.grid_forget()
            self.main_frm.grid_remove()
            # self.root.after_idle(self.root.event_generate, '<Configure>')
            # self.root.event_generate('<Configure>')
            self.root.update()
            # self.main_frm.destroy()





    def recurse_tk_structure(self, obj, name='starting_level', indent=0):
        """Recursively move down the nested tkinter objects by their 'children' attribute, printing the structure.

        :param obj: tkinter object.
        :param name: the 'key' from the next level up dict for this object.
        :param indent: how far to indent the print statement.
        """
        ind_space = ' ' * indent
        print(f'{ind_space}{name} - {obj}')

        try:
            for name, kid in obj.children.items():
                self.recurse_tk_structure(kid, name, indent + 4)
        except AttributeError:
            print(f'{ind_space}leaf - end')

    def wigify(self, obj):
        """Add a property 'wgts' that is an empty dictionary to the obj. (Intended for keeping track of tkinter widgets.)

        :param obj: any, the object to add the property.
        """
        setattr(obj, 'wgts', {})

    def recurse_hover(self, wgts_dict, indent=0):
        """Recursively move down the nested tk objects by their 'custom' .wgt dict items adding a mouse-over function.

        :param wgts_dict:
        :param indent:
        """
        for wname, wgt in wgts_dict.items():
            print('wd' + '\t' * indent, wgt, wgt.grid_info())
            # if 'frame' not in wname:
            #     print(f'I am not a frame {wname}!')
            #     me.hover_enter_factory(wgt)
            # else:
            #     print(f'I am a frame {wname}!')
            self.hover_enter_factory(wgt)
            try:
                sub_wgts = getattr(wgt, 'wgts')
                if sub_wgts is not None:
                    self.recurse_hover(sub_wgts, indent=indent + 4)
            except AttributeError:
                pass

    def hover_enter_factory(self, this_widget):
        """Bind a mouse-hover function to a tkinter widget to display information when hovered.

        :param this_widget: a tkinter widget.
        """
        # print(this_widget)
        this_widget = this_widget
        winfo = this_widget.grid_info()

        def set_loc_label(event, this_widget):
            event_widget = event.widget
            # self.wgts['dev_label'].config(text=f'{winfo}')
            print(this_widget, event_widget, winfo)

        import functools

        this_fn = functools.partial(set_loc_label, this_widget=this_widget)

        this_widget.bind("<Enter>", this_fn)

    def styling(self):
        """Set the styling elements of the window.

        """
        self.root.tk.call("source", "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl")
        self.root.tk.call("set_theme", "dark")
        # frame padding
        self.pad = dict(
            x=5,
            y=3
        )
        self._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': 'Card.TFrame'}

        # looking at hiding the titlebar, no luck
        # me.root.wm_attributes('-fullscreen', 'True')  # fullscreen no titlebar
        # me.root.attributes('-fullscreen', 'True')  # same as with wm_
        # me.root.wm_attributes('-type', 'splash')  # linux specific
        # me.root.overrideredirect(1)  # this hides the titlebar, but it's placing the window in the corner

    def to_the_front(self):
        raise_above_all(self.root)

def raise_above_all(window):
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)


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


def get_dummy_dict(oospec_len_meters, template_str='At {timestamp}\nthere were {len_meters} meters oospec!', msg_count=5):
    return {'messages': [{'title': 'Out of spec!',
                          'msg_txt': {'template': template_str,
                                      'timestamp': datetime.now().isoformat(),
                                      'length_in_meters': oospec_len_meters},
                          'buttons': ['removed!', 'oops!'],
                          'toggle_count_guess': mnum + 1,
                          'msg_id': msg_id
                          }
                         for mnum, msg_id in
                         enumerate(('msg123', 'msg456', 'msg789', 'msg987', 'msg654'))],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


if __name__ == '__main__':
    # if called from the command line (over ssl) parse the json to a dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument('--pup_json', help='A json string defining the popups to display.')
    args = parser.parse_args()
    json_str = args.pup_json

    dev_popup()
