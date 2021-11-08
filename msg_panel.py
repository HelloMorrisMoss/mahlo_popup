import tkinter as tk
from datetime import datetime
from tkinter import ttk

import logging


lg = logging.getLogger('mds_popup_window')
logging.basicConfig()


class MessagePanel:
    def __init__(self, parent, message, row, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        # self.dt_format_str = dt_format_str
        message['msg_txt']['timestamp'] = datetime.fromisoformat(message['msg_txt']['timestamp'])
        self.main_frame = tk.ttk.LabelFrame(parent, text=message['title'])  # , style='Card.TFrame')
        # self.main_frm.wgts[message['msg_id']] = mlf
        # self.wigify(mlf)
        self._removed_vals = {'all': tk.StringVar(), 'left': tk.StringVar(), 'left_center': tk.StringVar(), 'center': tk.StringVar(), 'right_center': tk.StringVar(), 'right': tk.StringVar()}
        self.add_message_display(self.main_frame, message)
        self.main_frame.grid(column=0, row=row, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
        self.add_buttons(self.main_frame, message)

    def add_message_display(self, parent, message):
        msg = message['msg_txt']
        message_text = msg['template'].format(timestamp=msg['timestamp'].strftime(self.dt_format_str), len_meters=msg['length_in_meters'])
        label = tk.ttk.Label(parent, text=message_text)
        label.grid(column=0, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="w")
        # parent.wgts['msg_box'] = label

    def add_buttons(self, parent, message):
        """Add the button frames and their widgets to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        self._add_removed_toggle_selectors(message, parent)

        # add the save button
        send_button_frame = tk.ttk.Frame(parent, style=self._wgt_styles['labelframe'])

        send_grid_params = {'column': 12, 'row': 0, 'padx': self.pad['x'],
                                                   'pady': self.pad['y'],
                                                   'sticky': 'nesw',
                            'rowspan': 2}
        send_button_frame.grid(**send_grid_params)
        # self.wigify(send_button_frame)
        # parent.wgts[f'send_button_frame'] = send_button_frame
        send_btn = tk.ttk.Button(send_button_frame, style='Accent.TButton', text='Save')
        send_btn.grid(**send_grid_params)
        setattr(send_btn, 'msg_id', message['msg_id'])
        setattr(send_btn, 'side', 'send')

    def send_response(self, event):
        msg_id = self._get_event_info(event)
        # removed_results_dict = {side: self.main_frm.wgts[msg_id].wgts[side].state_var.get() for side in ('left', 'center', 'right')}
        removed_results_dict = self._removed_state_vars[msg_id]
        # TODO: save to sqlite database, then try to send all items unsent in the db

    def _add_removed_toggle_selectors(self, message, parent):
        """Add the toggle buttons frame to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        # the toggle button frame
        btn_frame = tk.ttk.Frame(parent, style=self._wgt_styles['labelframe'])  # is this style hiding the frame?
        btn_frame.grid(column=1, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
        # self.wigify(btn_frame)
        # parent.wgts[f'btn_frame_main'] = btn_frame

        self.button_def_dict = self._get_toggle_definitions(message['toggle_count_guess'])

        # add them to the button frame
        for bnum, (btn, btndef) in enumerate(self.button_def_dict.items()):
            self._add_toggle(btn_frame, btn, btndef, message, parent)

        # add a line separator to make the all button stand out from the side buttons
        sep = ttk.Separator(btn_frame, orient='horizontal')
        sep_grid_dict = {'column': 0,
                         'row': 1,
                         'columnspan': 12,
                         'padx': self.pad['x'],
                         'pady': self.pad['y'],
                         'sticky': 'nesw'}
        sep.grid(**sep_grid_dict)

    def _add_toggle(self, btn_frame, btn, btndef, message, parent):
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

        # if it is the 'all' button add the list of buttons to toggle
        if btndef.get('not_all_list') is not None:
            lg.debug('setting not_all_list on all button')
            setattr(btn_wgt, 'not_all_list', btndef['not_all_list'])

        # add the event handler method
        btn_wgt.bind('<Button-1>', self.toggle_changes_event_handler)

        # TODO: only the sections that should have been removed to default on (from the 'message')
        # default to all toggles on
        btndef['params']['variable'].set(True)

        # add it to the wgts dict
        # parent.wgts[btn] = btn_wgt

    def _get_toggle_definitions(self, num_of_buttons=3):
        """Get the dictionary defining the 'all' and 'left', 'center', and 'right' sides' toggle buttons.

        :return: dict, the definition dictionary.
        """
        # define the sides buttons
        number_of_buttons_to_definitions_lists = {1: [], 2: ['left', 'right'], 3: ['left', 'center', 'right'],
                                            4: ['left', 'left_center', 'right_center', 'right'],
                                            5: ['left', 'left_center', 'center', 'right_center', 'right']}
        side_button_text = {'left': 'Operator\nSide', 'left_center': 'Operator Side\nof Center',
                            'center': 'Center\n', 'right_center': 'Foamline Side\nof Center', 'right': 'Foamline\nSide'}
        side_button_dict = {side: {'params':
                                       {'text': f'{side_button_text[side]} was removed.',
                                        'variable': tk.IntVar()},
                                   'grid_params': {'column': 2 * (n + 1), 'columnspan': 2, 'rowspan': 2,
                                                   'row': 2, 'padx': self.pad['x'], 'pady': self.pad['y']},
                                   'not_all_list': number_of_buttons_to_definitions_lists[num_of_buttons]
                                   } for n, side in enumerate(number_of_buttons_to_definitions_lists[num_of_buttons])}

        # define the 'all of the section removed' button
        all_button_column = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
        button_def_dict = {'all': {'params': {'text': 'All of this length was removed.',
                                              'command': lambda: lg.debug('You press my buttons!'),
                                              'variable': tk.IntVar()},
                                   'grid_params': {'column': all_button_column[num_of_buttons],
                                                   'row': 0,
                                                   'columnspan': 3,
                                                   'padx': self.pad['x'],
                                                   'pady': self.pad['y'],
                                                   'sticky': 'nesw'},
                                   'not_all_list': number_of_buttons_to_definitions_lists[num_of_buttons]}}
        button_def_dict.update(side_button_dict)
        return button_def_dict

    def toggle_changes_event_handler(self, event):
        """Handle the toggle button being changed with regard to its designation and the state of the other toggles.

        If the 'all' button is turned on or off set the 'sides' to the same.
        If all of the 'sides' are turned on set the 'all' to the same.
        If any of the 'sides' are turned off, turn off the 'all'.

        :param event: tkinter.Event, for the toggle button being pressed.
        """
        msg_id, now_on, side = self._get_event_info(event)
        lg.debug(event, event.widget.msg_id, event.widget.side, event.widget.state_var.get(), event.widget.state(),
              f'new {now_on}')

        # the sides that are not all
        # not_all = 'left', 'center', 'right'
        not_all = event.widget.not_all_list

        # evaluate and set the toggles if needed
        if side == 'all':
            if now_on:
                lg.debug('set sides true')
                self._set_all_sides(not_all, True)
            else:
                lg.debug('set sides false')
                self._set_all_sides(not_all, False)
        else:
            lg.debug('a side was changed')
            if not now_on:
                lg.debug('set all toggle-button false since this is not true')
                if self.main_frame.wgts[msg_id].wgts['all'].state_var.get():
                    self._set_all_sides(('all',), False)
            else:
                lg.debug('a side was set to true')
                sides_count = 0

                for iter_side in not_all:
                    # if this is the side
                    if side == iter_side:
                        sides_count += 1
                        side_val = 1
                    else:
                        side_val = self._removed_vals.get(iter_side).get()
                        sides_count += 'was removed' in side_val
                    lg.debug(iter_side, side_val, sides_count)

                if sides_count == len(event.widget.not_all_list):
                    self._set_all_sides(('all',), True)

    def _set_all_sides(self, not_all, state):
        """Set all the side buttons to the same state.

        :param not_all: list, of strings defining the sides other than 'all'
        :param state: any, the state to set the variable to.
        """
        if state:
            set_value = 'onvalue'
        else:
            set_value = 'offvalue'

        for side in not_all:
            set_str = self.button_def_dict[side][set_value]
            self._removed_vals[side].set(set_str)

    def _get_event_info(self, event):
        """Get the side, new state, and message id from the widget calling the event.

        :param event: tkinter.Event, the button press event.
        :return: tuple, of the info.
        """
        msg_id = event.widget.msg_id  # the custom id attribute, used to track which message this relates to
        try:
            side = event.widget.side  # left, right, center, all
            now_on = 'selected' not in event.widget.state()  # whether the toggle is turning on or off; was selected -> off
        except AttributeError:
            # TODO: make this function better
            # it must have been the send button
            return msg_id

        return msg_id, now_on, side

    def button_command(self):
        pass

    def add_toggle(self, button, side):
        # add a state tracker on the button, a side metadata-label, and add a side state tracker to the message frame
        setattr(button, 'active', True)
        setattr(button, 'side', side)
        setattr(button.master.master, side, True)

        def toggle_me(*args, **kwargs):
            lg.debug('args', args)
            lg.debug('kwargs', kwargs)
            # button = button
            button = args[0].widget
            lg.debug(f'button background was {button.cget("background")}')
            if button.active:
                lg.debug(f'{button.side} button was active, now setting to inactive')
                button.active = False
                setattr(button.master.master, button.side, False)
                button.config(background='SystemButtonFace')
            else:
                lg.debug(f'{button.side} button was inactive, now setting to active')
                button.active = True
                setattr(button.master.master, button.side, True)
                button.config(background='blue')

        button.bind("<Button-1>", toggle_me)
        # return toggle_me