"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import argparse
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pprint import pprint  # for dev


class Popup:
    """A popup window with messages to respond to. Creats the window and messages based on a provided dictionary.

    """

    def __init__(self, input_dict):
        # set things up for the main window
        self._defdic = input_dict
        self.root = tk.Tk()
        self.root.title(self._defdic['main_win']['title'])
        self.root.geometry('800x500')
        self.wgts = {}
        self.styling()

        self._removed_state_vars = {
            msg['msg_id']: {'all': tk.IntVar(), 'left': tk.IntVar(), 'center': tk.IntVar(), 'right': tk.IntVar()}
            for msg in self._defdic['messages']}
        for mid, state_dict in self._removed_state_vars.items():
            state_dict['all'].set(True)

        # dev_frame = tk.ttk.LabelFrame(me.root, text='Test frame')
        # dev_frame.grid(row=0, column=0)
        # dev_label = tk.ttk.Label(dev_frame, text='for dev')
        # dev_label.grid(row=0, column=0)
        #
        # me.wgts['dev_label'] = dev_label

        self.main_frm = tk.ttk.Frame(self.root)
        self.main_frm.grid(row=1, column=0, sticky='nesw', columnspan=3)
        self.wigify(self.main_frm)
        # me.hover_enter_factory(me.main_frm)
        self.wgts['main_frame'] = self.main_frm

        # add the frames for the messages and the widgets therein
        for mnum, message in enumerate(self._defdic['messages']):
            message['msg_txt']['timestamp'] = datetime.fromisoformat(message['msg_txt']['timestamp'])
            mlf = tk.ttk.LabelFrame(self.main_frm, text=message['title'])  # , style='Card.TFrame')
            self.main_frm.wgts[message['msg_id']] = mlf
            self.wigify(mlf)
            self.add_message_display(mlf, message)
            mlf.grid(column=0, row=mnum, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
            self.add_buttons(mlf, message)

        # me.recurse_hover(me.wgts)
        self.recurse_tk_structure(self.root)

        self.root.mainloop()

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

    def add_message_display(self, parent, message):
        msg = message['msg_txt']
        message_text = msg['template'].format(timestamp=msg['timestamp'], len_meters=msg['length_in_meters'])
        label = tk.ttk.Label(parent, text=message_text)
        label.grid(column=0, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="w")
        parent.wgts['msg_box'] = label

    def button_command(self):
        pass

    def add_toggle(self, button, side):
        # add a state tracker on the button, a side metadata-label, and add a side state tracker to the message frame
        setattr(button, 'active', True)
        setattr(button, 'side', side)
        setattr(button.master.master, side, True)

        def toggle_me(*args, **kwargs):
            print('args', args)
            print('kwargs', kwargs)
            # button = button
            button = args[0].widget
            print(f'button background was {button.cget("background")}')
            if button.active:
                print(f'{button.side} button was active, now setting to inactive')
                button.active = False
                setattr(button.master.master, button.side, False)
                button.config(background='SystemButtonFace')
            else:
                print(f'{button.side} button was inactive, now setting to active')
                button.active = True
                setattr(button.master.master, button.side, True)
                button.config(background='blue')

        button.bind("<Button-1>", toggle_me)
        # return toggle_me

    def toggle_changes_event_handler(self, event):
        """Handle the toggle button being changed with regard to its designation and the state of the other toggles.

        If the 'all' button is turned on or off set the 'sides' to the same.
        If all of the 'sides' are turned on set the 'all' to the same.
        If any of the 'sides' are turned off, turn off the 'all'.

        :param event: tkinter.Event, for the toggle button being pressed.
        """
        msg_id, now_on, side = self._get_event_info(event)
        print(event, event.widget.msg_id, event.widget.side, event.widget.state_var.get(), event.widget.state(),
              f'new {now_on}')

        # the sides that are not all
        not_all = 'left', 'center', 'right'

        # evaluate and set the toggles if needed
        if side == 'all':
            if now_on:
                print('set sides true')
                self._set_all_sides(msg_id, not_all, True)
            else:
                print('set sides false')
                self._set_all_sides(msg_id, not_all, False)
        else:
            print('a side was changed')
            if not now_on:
                print('set all toggle-button false since this is not true')
                if self.main_frm.wgts[msg_id].wgts['all'].state_var.get():
                    self.main_frm.wgts[msg_id].wgts['all'].state_var.set(False)
            else:
                print('a side was set to true')
                sides_count = 0

                for iter_side in not_all:
                    if side == iter_side:
                        sides_count += 1
                        side_val = 1
                    else:
                        side_val = self.main_frm.wgts[msg_id].wgts[iter_side].state_var.get()
                        sides_count += side_val
                    print(iter_side, side_val, sides_count)

                if sides_count == 3:
                    self.main_frm.wgts[msg_id].wgts['all'].state_var.set(True)

    def _set_all_sides(self, msg_id, not_all, state):
        """Set all the side buttons to the same state.

        :param msg_id: str, the id of the message these buttons belong to.
        :param not_all: list, of strings defining the sides other than 'all'
        :param state: bool, the state to set the toggle tkinter.IntVar to.
        """
        for val in not_all:
            self.main_frm.wgts[msg_id].wgts[val].state_var.set(state)

    def _get_event_info(self, event):
        """Get the side, new state, and message id from the widget calling the event.

        :param event: tkinter.Event, the button press event.
        :return: tuple, of the info.
        """
        side = event.widget.side  # left, right, center, all
        now_on = 'selected' not in event.widget.state()  # whether the toggle is turning on or off; was selected -> off
        msg_id = event.widget.msg_id  # the custom id attribute, used to track which message this relates to
        return msg_id, now_on, side

    def add_buttons(self, parent, message):
        """Add the button frames and their widgets to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        self._add_removed_toggle_selectors(message, parent)

    def _add_removed_toggle_selectors(self, message, parent):
        """Add the toggle buttons frame to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        # the toggle button frame
        btn_frame = tk.ttk.Frame(parent, style=self._wgt_styles['labelframe'])  # is this style hiding the frame?
        btn_frame.grid(column=1, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
        self.wigify(btn_frame)
        parent.wgts[f'btn_frame_main'] = btn_frame

        button_def_dict = self._get_toggle_definitions()

        # add them to the button frame
        for bnum, (btn, btndef) in enumerate(button_def_dict.items()):
            self._add_toggle(btn_frame, btn, btndef, message)

        # add a line separator to make the all button stand out from the side buttons
        sep = ttk.Separator(btn_frame, orient='horizontal')
        sep_grid_dict = {'column': 0,
                         'row': 1,
                         'columnspan': 8,
                         'padx': self.pad['x'],
                         'pady': self.pad['y'],
                         'sticky': 'nesw'}
        sep.grid(**sep_grid_dict)

    def _add_toggle(self, btn_frame, btn, btndef, message):
        """Add a toggle button to the frame using a definition dictionary.

        :param btn_frame: tkinter.Frame
        :param btn: str, the 'side' for the button.
        :param btndef: dict, definining parameters for the button.
        :param message: dict, the message definition.
        """
        # add a toggle switch
        btn_wgt = ttk.Checkbutton(btn_frame, style=self._wgt_styles['toggle'], **btndef['params'])
        btn_wgt.grid(**btndef['grid_params'])

        # add some custom attributes to use elsewhere, to keep track of which button is which
        setattr(btn_wgt, 'state_var', btndef['params']['variable'])
        setattr(btn_wgt, 'side', btn)
        setattr(btn_wgt, 'msg_id', message['msg_id'])

        # add the event handler method
        btn_wgt.bind('<Button-1>', self.toggle_changes_event_handler)

        # TODO: only the sections that should have been removed to default on (from the 'message')
        # default to all toggles on
        btndef['params']['variable'].set(True)

        # add it to the wgts dict
        btn_frame.wgts[btn] = btn_wgt

    def _get_toggle_definitions(self):
        """Get the dictionary defining the 'all' and 'left', 'center', and 'right' sides' toggle buttons.

        :return: dict, the definition dictionary.
        """
        # define the 'all of the section removed' button
        button_def_dict = {'all': {'params': {'text': 'All of this length was removed.',
                                              'command': lambda: print('You press my buttons!'),
                                              'variable': tk.IntVar()},
                                   'grid_params': {'column': 4,
                                                   'row': 0,
                                                   # 'columnspan': 8,
                                                   'padx': self.pad['x'],
                                                   'pady': self.pad['y'],
                                                   'sticky': 'nesw'}}}
        # define the sides buttons
        side_button_text = {'left': 'Operator\nSide', 'center': 'Center\n', 'right': 'Foamline\nSide'}
        side_button_dict = {side: {'params':
                                       {'text': f'{side_button_text[side]} was removed.',
                                        'variable': tk.IntVar()},
                                   'grid_params': {'column': 2 * (n + 1), 'columnspan': 2, 'rowspan': 2,
                                                   'row': 2, 'padx': self.pad['x'], 'pady': self.pad['y']}
                                   } for n, side in enumerate(('left', 'center', 'right'))}
        button_def_dict.update(side_button_dict)
        return button_def_dict


# TODO:
#  need to talk to some operators about how long until it makes sense to popup
#  doing it too soon they wouldn't have a chance and could be disruptive
#  respond (send it to a database?)
#  check that this will work over ssl (opening in the normal session) otherwise probably flask


if __name__ == '__main__':
    # if called from the command line (over ssl) parse the json to a dictionary
    parser = argparse.ArgumentParser()
    parser.add_argument('--pup_json', help='A json string defining the popups to display.')
    args = parser.parse_args()
    json_str = args.pup_json

    # for development, a dummy dict
    if json_str is None:
        oospec_len_meters = 4.3
        template_str = 'At {timestamp}\n there were {len_meters} meters oospec!'
        test_json_dict = {'messages': [{'title': 'Out of spec!',
                                        'msg_txt': {'template': template_str,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'length_in_meters': oospec_len_meters},
                                        'buttons': ['removed!', 'oops!'],
                                        'msg_id': msg_id
                                        }
                                       for msg_id in ('msg123', 'msg456', 'msg789')],
                          'main_win': {'title': 'Messages received!'}
                          }
        json_str = json.dumps(test_json_dict)

    pup_dict = json.loads(json_str)

    pup = Popup(pup_dict)
