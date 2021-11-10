import tkinter as tk
from datetime import datetime
from tkinter import ttk

import logging

lg = logging.getLogger('mds_popup_window')
lg.debug('logging in msg_panel')


class NumberPrompt(tk.Toplevel):
    """Show a tk popup window prompting for a number between 1 and 5, returning that value when pressed. Cancel as 0."""
    def __init__(self, parent, prompt=None):
        tk.Toplevel.__init__(self, parent)
        # def prompt_number_window(root):
        #         pwin = tk.Toplevel(root)
        row = 0
        # col = 0
        for col in range(0, 6):
            button_label_text = str(col) if col != 0 else 'Cancel'
            num_button = tk.ttk.Button(self, text=button_label_text)
            num_button.bind('<Button-1>', self.return_button_val)
            num_button.grid(row=row, column=col)
        self.value = tk.IntVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
        try:
            self.value.set(int(event.widget['text']))
        except ValueError:
            self.value.set(0)
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.focus_force()
        self.wait_window()
        return self.value.get()


if __name__ == '__main__':
    root = tk.Tk()
    prompt_val = NumberPrompt(root, '').show()
    lg.debug('prompt returned %s', prompt_val)
    print(prompt_val)


class MessagePanel:
    def __init__(self, root, parent, message, row, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        # self.dt_format_str = dt_format_str
        self._root = root
        self.message = message
        self.message['msg_txt']['timestamp'] = datetime.fromisoformat(message['msg_txt']['timestamp'])
        self.main_frame = tk.ttk.LabelFrame(parent, text=message['title'])  # , style='Card.TFrame')
        # self.main_frm.wgts[message['msg_id']] = mlf
        # self.wigify(mlf)
        self._removed_vals = {'all': tk.StringVar(), 'left': tk.StringVar(), 'left_center': tk.StringVar(), 'center': tk.StringVar(), 'right_center': tk.StringVar(), 'right': tk.StringVar()}

        self.add_message_display(self.main_frame, message)
        self.main_frame.grid(column=0, row=row, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
        self.add_buttons(self.main_frame, message)

    def add_message_display(self, parent, message):
        msg = message['msg_txt']
        message_text = msg['template'].format(timestamp=msg['timestamp'].strftime(self.dt_format_str),
                                              len_meters=msg['length_in_meters'])
        label = tk.ttk.Label(parent, text=message_text)
        label.grid(column=0, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="w")
        # parent.wgts['msg_box'] = label

    def add_buttons(self, parent, message):
        """Add the button frames and their widgets to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        # TODO: it may be worthwhile at some point to extract the toggle panel to its own class
        # add the removed foam toggles
        self._add_foam_removed_toggle_selectors(parent, message)

        # add the save button
        self.add_action_buttons(message, parent)

    def add_action_buttons(self, message, parent):
        """Add the action button frame and buttons.

        :param message:
        :param parent:
        """

        send_button_frame = tk.ttk.Frame(parent, style=self._wgt_styles['labelframe'])
        send_grid_params = {'column': 12, 'row': 0, 'padx': self.pad['x'],
                            'pady': self.pad['y'],
                            'sticky': 'nesw',
                            'columnspan': 2}
        send_button_frame.grid(**send_grid_params)
        self.add_save_button(send_button_frame, message, send_grid_params)

        # add the prompt for roll count change button
        num_button = tk.ttk.Button(send_button_frame, style='Accent.TButton', text='# of Rolls', command=self.prompt_for_rolls_count)
        send_grid_params.update(row=1)

        num_button.grid(**send_grid_params)

    def prompt_for_rolls_count(self):
        """Prompt for the number of rolls and change the toggles to match. Do nothing if cancel is selected."""

        new_count = NumberPrompt(self._root).show()
        if new_count:
            self.change_toggle_count(new_count)

    def add_save_button(self, parent, message, send_grid_params):
        """Add the save/send button.

        :param message:
        :param parent:
        :param send_grid_params:
        """
        send_btn = tk.ttk.Button(parent, style='Accent.TButton', text='Save')
        send_btn.grid(**send_grid_params)
        setattr(send_btn, 'msg_id', message['msg_id'])
        setattr(send_btn, 'side', 'send')

    def send_response(self, event):
        msg_id = self._get_event_info(event)
        # removed_results_dict = {side: self.main_frm.wgts[msg_id].wgts[side].state_var.get() for side in ('left', 'center', 'right')}
        removed_results_dict = self._removed_state_vars[msg_id]
        # TODO: save to sqlite database, then try to send all items unsent in the db

    def _add_foam_removed_toggle_selectors(self, parent, message, number_of_buttons=None):
        """Add the toggle buttons frame to the parent frame.

        :param message: dict, the message dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        # the toggle button frame
        self.btn_frame = tk.ttk.Frame(parent,
                                      style=self._wgt_styles['labelframe'])  # is this style hiding the frame?
        self.btn_frame.grid(column=1, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")
        # self.wigify(btn_frame)
        # parent.wgts[f'btn_frame_main'] = btn_frame

        # default to the guessed number
        if number_of_buttons is None:
            number_of_buttons = message['toggle_count_guess']

        self.toggle_button_def_dict = self._get_toggle_definitions(number_of_buttons)

        self._toggle_refs = {}

        # add them to the button frame
        for bnum, (btn, btndef) in enumerate(self.toggle_button_def_dict.items()):
            self._toggle_refs[btn] = self._add_toggle(self.btn_frame, btn, btndef, message, parent)

        # add a line separator to make the all button stand out from the side buttons
        sep = ttk.Separator(self.btn_frame, orient='horizontal')
        sep_grid_dict = {'column': 0,
                         'row': 1,
                         'columnspan': 12,
                         'padx': self.pad['x'],
                         'pady': self.pad['y'],
                         'sticky': 'nesw'}
        sep.grid(**sep_grid_dict)

    def _add_toggle(self, btn_frame, btn_side, btndef, message, parent):
        """Add a toggle button to the frame using a definition dictionary.

        :param btn_frame: tkinter.Frame
        :param btn_side: str, the 'side' for the button.
        :param btndef: dict, definining parameters for the button.
        :param message: dict, the message definition.
        """
        # add a toggle switch
        btn_wgt = ttk.Checkbutton(btn_frame, style=self._wgt_styles['toggle'], **btndef['params'])
        btn_wgt.grid(**btndef['grid_params'])

        # add some custom attributes to use elsewhere, to keep track of which button is which
        setattr(btn_wgt, 'state_var', btndef['params']['variable'])
        setattr(btn_wgt, 'side', btn_side)
        setattr(btn_wgt, 'msg_id', message['msg_id'])
        # setattr(btn_wgt, 'onvalue', btndef['params']['onvalue'])
        # setattr(btn_wgt, 'offvalue', btndef['params']['offvalue'])

        # if it is the 'all' button add the list of buttons to toggle
        if btndef.get('not_all_list') is not None:
            # lg.debug('setting not_all_list on all button')
            setattr(btn_wgt, 'not_all_list', btndef['not_all_list'])

        # add the event handler method
        btn_wgt.bind('<Button-1>', self.toggle_changes_event_handler)

        # TODO: only the sections that should have been removed to default on (from the 'message')
        # default to all toggles on
        btndef['params']['variable'].set(btndef['params']['onvalue'])

        # add it to the wgts dict
        # parent.wgts[btn_side] = btn_wgt
        return btn_wgt

    def _get_toggle_definitions(self, num_of_buttons=3):
        """Get the dictionary defining the 'all' and 'left', 'center', and 'right' sides' toggle buttons.

        :return: dict, the definition dictionary.
        """
        # define the sides buttons
        number_of_buttons_to_definitions_lists = {1: [], 2: ['left', 'right'], 3: ['left', 'center', 'right'],
                                                  4: ['left', 'left_center', 'right_center', 'right'],
                                                  5: ['left', 'left_center', 'center', 'right_center', 'right']}
        self.not_all_list = number_of_buttons_to_definitions_lists[num_of_buttons]
        side_button_text = {'left': 'Operator Side\n', 'left_center': 'Operator Side of Center\n',
                            'center': 'Center of Foam\n', 'right_center': 'Foamline Side of Center\n', 'right': 'Foamline Side\n'}
        side_button_dict = {side: {'params':
                                       {'onvalue': f'{side_button_text[side]} WAS removed.',
                                        'offvalue': f'{side_button_text[side]} NOT removed.',
                                        'textvariable': self._removed_vals[side]},
                                   'grid_params': {'column': 2 * (n + 1), 'columnspan': 2, 'rowspan': 2,
                                                   'row': 2, 'padx': self.pad['x'], 'pady': self.pad['y']},
                                   'not_all_list': number_of_buttons_to_definitions_lists[num_of_buttons]
                                   } for n, side in
                            enumerate(number_of_buttons_to_definitions_lists[num_of_buttons])}

        # define the 'all of the section removed' button
        all_button_column = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}  # the column needs to be dynamic or it will be off center
        button_def_dict = {'all': {'params': {'text': 'All of this length was removed.',
                                              'command': lambda: lg.debug('You press my buttons!'),
                                              'onvalue': 'ALL of this length was removed.',
                                              'offvalue': 'NOT all of this length was removed.',
                                              'textvariable': self._removed_vals['all']},
                                   'grid_params': {'column': all_button_column[num_of_buttons],
                                                   'row': 0,
                                                   'columnspan': 3,
                                                   'padx': self.pad['x'],
                                                   'pady': self.pad['y'],
                                                   'sticky': 'nesw'}
                                   }}
        button_def_dict.update(side_button_dict)
        for btndf in button_def_dict.values():
            btndf['params']['variable'] = btndf['params']['textvariable']
            # btndf['params']['textvariable'].set(btndf['params']['onvalue'])
        return button_def_dict

    def destroy_toggle_panel(self):
        """Destroy the current button framer for this message panel."""
        self.btn_frame.destroy()

    def change_toggle_count(self, new_count):
        """Change the number of toggle-buttons on the the foam removed toggles frame.

        :param new_count: int, the number of toggles to use.
        """
        self.destroy_toggle_panel()
        self._add_foam_removed_toggle_selectors(self.main_frame, self.message, new_count)

    def toggle_changes_event_handler(self, event):
        """Handle the toggle button being changed with regard to its designation and the state of the other toggles.

        If the 'all' button is turned on or off set the 'sides' to the same.
        If all of the 'sides' are turned on set the 'all' to the same.
        If any of the 'sides' are turned off, turn off the 'all'.

        :param event: tkinter.Event, for the toggle button being pressed.
        """
        msg_id, now_on, side = self._get_event_info(event)

        # this is just for development
        dbg_vars = event, event.widget.msg_id, event.widget.side,\
                   event.widget.state_var.get(), event.widget.state(), f'new {now_on}'
        lg.debug('%s, ' * len(dbg_vars), *dbg_vars)


        # evaluate and set the toggles if needed
        if side == 'all':
            if now_on:
                # set sides true
                self._set_all_sides(self.not_all_list, True)
            else:
                # set sides false
                self._set_all_sides(self.not_all_list, False)
        else:
            # a side was changed
            if not now_on:
                # set all toggle-button false since this is not true
                self._set_all_sides(('all',), False)
            else:
                # a side was set to true
                sides_count = 0

                for iter_side in self.not_all_list:
                    # if this is the side
                    if side == iter_side:
                        sides_count += 1
                        side_val = 1
                    else:
                        # count the sides that are true
                        side_val = self._removed_vals.get(iter_side).get()
                        sides_count += 'WAS removed' in side_val
                    lg.debug('iter_side %s, side_val %s, sides_count %s', iter_side, side_val, sides_count)

                if sides_count == len(self.not_all_list):
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
            set_str = self.toggle_button_def_dict[side]['params'][set_value]
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
        setattr(button, 'side', side)

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
