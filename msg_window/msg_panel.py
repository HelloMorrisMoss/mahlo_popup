import tkinter as tk
from datetime import datetime
from tkinter import ttk

from dev_common import StrCol
from log_setup import lg
from msg_window.defect_attributes import DefectTypePanel, LengthSetFrames, NumberPrompt


class MessagePanel(tk.ttk.LabelFrame):
    def __init__(self, parent, defect_instance=None, row=0, **kwargs):
        super().__init__(parent)
        self.config(text=f'Defect #{defect_instance.id}')
        self.msg_number = row
        if not kwargs.get('pad'):
            kwargs['pad'] = {'x': 2, 'y': 2}
        if not kwargs.get('dt_format_str'):
            self.dt_format_str = r'%I:%M %d-%b'
        self.grid_params_ = dict(column=0, row=row, padx=kwargs['pad']['x'], pady=kwargs['pad']['y'], sticky="nesw")
        self.grid(**self.grid_params_)
        self.parent = parent

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.hideables = []
        self.defect_interface = defect_instance
        self.defect_id = self.defect_interface.id
        self.message_text_template = '{timestamp} on lam{lam_num}\n{len_meters} meters oospec\n' \
                                     'starting at Mahlo {mahlo_start_length}\n' \
                                     'due to {dtype}\ndefect id: {defect_id}'

        sides_to_defect_columns_dict = {'left': 'rem_l', 'left_center': 'rem_lc',
                                        'center': 'rem_c', 'right_center': 'rem_rc', 'right': 'rem_r'}

        self._removed_vals = {k: StrCol(self.defect_interface, col) for k, col in sides_to_defect_columns_dict.items()}
        self._removed_vals.update({'all': tk.StringVar()})

        # add the tabbed frames
        self._tabframe = ttk.Notebook(self)
        self._tabframe.grid(row=0, column=0)

        self._lot_rolls_type_frame = ttk.Frame(self)
        self._lengths_frame = ttk.Frame(self)
        self._confirm_frame = ttk.Frame(self)

        self._tabframe.add(self._lot_rolls_type_frame, text='lot #, rolls, defect type')
        self._tabframe.add(self._lengths_frame, text='lengths')
        self._tabframe.add(self._confirm_frame, text='confirmation')

        # if it's an auto-detected defect, they hopefully only need to confirm it, start there
        if self.defect_interface.record_creation_source != 'operator':
            self._tabframe.select(self._tabframe.index('end') - 1)

        # the label that displays the defect_instance info
        self.message_label = self._add_message_display_label(self._confirm_frame)
        self.update_message_text()
        self.hideables.append(self.message_label)

        self._add_buttons(self._confirm_frame)

        self.defect_type_panel = DefectTypePanel(self._lot_rolls_type_frame, self.defect_interface)
        self.defect_type_panel.grid(row=0, column=0)

        self._roll_count_selector = NumberPrompt(self._lot_rolls_type_frame, self.defect_interface)
        self._roll_count_selector.grid(row=1, column=0)

        self.length_panel = LengthSetFrames(self._lengths_frame, self.defect_interface)
        self.length_panel.grid(row=0, column=0, sticky='nesw')

    def _add_message_display_label(self, parent):
        """A ttk label displaying information about the defect. Clicking the label will allow changes to be made.

        :param parent: tkinter container, the parent container to add the label to.
        :return: tk.ttk.Label
        """

        label = tk.ttk.Label(parent)
        grid_params = dict(column=0, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="w")
        setattr(label, 'grid_params_', grid_params)
        label.grid(**grid_params)

        # when clicked show the select attributes panel.
        label.bind('<Button-1>', self.change_attributes)

        return label

    # add a popup to change the defect attributes when clicking the label
    def change_attributes(self, event=None):
        lg.debug('changing defect type')
        self.defect_type_panel.grid()
        self.hide_hideables()

    def refresh_panel(self):
        self.update_message_text()
        self._change_toggle_count()

    def hide_hideables(self):
        """Hide (.remove_grid) on all widgets that have been added to the hideables list."""
        lg.debug('hideable: %s', self.hideables)
        for hideable in self.hideables:
            hideable.grid_remove()

    def show_hideables(self, event=None):
        """Hide (.remove_grid) on all widgets that have been added to the hideables list."""
        for hideable in self.hideables:
            lg.debug(hideable)
            hideable.grid(**hideable.grid_params_)

    def update_message_text(self):
        """Update the message label with any changes."""

        msg_text = self.message_text_template.format(
            timestamp=self.defect_interface.defect_end_ts.strftime(self.dt_format_str),
            len_meters=self.defect_interface.length_of_defect_meters,
            dtype=self.defect_interface.defect_type,
            defect_id=self.defect_interface.id,
            mahlo_start_length=self.defect_interface.mahlo_start_length,
            lam_num=self.defect_interface.lam_num,
            )
        self.message_label.config(text=msg_text)

    def _add_buttons(self, parent):
        """Add the button frames and their widgets to the parent frame.

        :param message: dict, the defect_instance dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """

        # TODO: it may be worthwhile at some point to extract the toggle panel to its own class
        # add the removed foam toggles
        self._add_foam_removed_toggle_selectors(parent)

        # add the save button
        self._add_action_buttons(parent)

    def _add_action_buttons(self, parent):
        """Add the action button frame and buttons.

        :param parent: tkinter container
        """

        send_button_frame = tk.ttk.Frame(parent, style=self._wgt_styles['labelframe'])
        send_grid_params = {'column': 12, 'row': 0, 'padx': self.pad['x'],
                            'pady': self.pad['y'],
                            'sticky': 'nesw',
                            'columnspan': 2}
        send_button_frame.grid(**send_grid_params)
        setattr(send_button_frame, 'grid_params_', send_grid_params)
        self.hideables.append(send_button_frame)
        self.add_save_button(send_button_frame, send_grid_params)

    def add_save_button(self, parent, send_grid_params):
        """Add the save/send button.

        :param parent: tkinter container
        :param send_grid_params: dict, kwargs for the buttons .grid method.
        """

        send_btn = tk.ttk.Button(parent, style='Accent.TButton', text='Save', command=self.save_response)
        send_btn.grid(**send_grid_params)
        setattr(send_btn, 'msg_id', self.defect_interface.id)
        setattr(send_btn, 'side', 'send')

    def save_response(self, event=None):
        """Save the changes made to the database.

        :param event: tkinter.Event, (optional)
        """
        # msg_id = self._get_event_info(event)
        # removed_results_dict = self._removed_state_vars[msg_id]
        lg.debug(self.defect_interface)
        now_ts = datetime.now()
        self.defect_interface.entry_modified_ts = now_ts
        self.defect_interface.operator_saved_time = now_ts

        # I don't love this parent.parent referencing, if the app changes (from flask being restarted) it would
        # automatically grab the new one if updated in the main window
        lg.debug(self.parent.current_defects)
        with self.parent.parent.flask_app.app_context():
            self.defect_interface.save_to_database()
            self.parent.current_defects.pop(self.parent.current_defects.index(self.defect_interface))
        self.destroy()
        lg.debug(self.parent.current_defects)
        # TODO: save to sqlite database, then try to send all items unsent in the db; does it have to be sqlite?
        #  can we just install postgres on the hmi? Retries may suffice, see how connection looks in production

    def _add_foam_removed_toggle_selectors(self, parent):
        """Add the toggle buttons frame to the parent frame.

        :param message: dict, the defect_instance dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """
        # the toggle button frame
        self.btn_frame = tk.ttk.Frame(parent,
                                      style=self._wgt_styles['labelframe'])  # is this style hiding the frame?
        grid_params = dict(column=1, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="nesw")

        setattr(self.btn_frame, 'grid_params_', grid_params)
        self.btn_frame.grid(**grid_params)
        self.hideables.append(self.btn_frame)

        # TODO: move the 'change number of rolls selector' to be with the rolls removed
        # default to the guessed number
        # number_of_buttons = defect_interface['toggle_count_guess']
        number_of_buttons = self.defect_interface.rolls_of_product_post_slit

        self.toggle_button_def_dict = self._get_toggle_definitions(number_of_buttons)

        self._toggle_refs = {}

        # add them to the button frame
        for bnum, (btn, btndef) in enumerate(self.toggle_button_def_dict.items()):
            self._toggle_refs[btn] = self._add_toggle(self.btn_frame, btn, btndef)

        # add a line separator to make the all button stand out from the side buttons
        sep = ttk.Separator(self.btn_frame, orient='horizontal')
        sep_grid_dict = {'column': 0,
                         'row': 1,
                         'columnspan': 12,
                         'padx': self.pad['x'],
                         'pady': self.pad['y'],
                         'sticky': 'nesw'}
        sep.grid(**sep_grid_dict)

    def _add_toggle(self, btn_frame, btn_side, btndef):
        """Add a toggle button to the frame using a definition dictionary.

        :param btn_frame: tkinter.Frame
        :param btn_side: str, the 'side' for the button.
        :param btndef: dict, definining parameters for the button.
        """
        # add a toggle switch
        btn_wgt = ttk.Checkbutton(btn_frame, style=self._wgt_styles['toggle'], **btndef['params'])
        btn_wgt.grid(**btndef['grid_params'])

        # add some custom attributes to use elsewhere, to keep track of which button is which
        setattr(btn_wgt, 'state_var', btndef['params']['variable'])
        setattr(btn_wgt, 'side', btn_side)
        setattr(btn_wgt, 'msg_id', self.defect_interface.id)

        # if it is the 'all' button add the list of buttons to toggle
        if btndef.get('not_all_list') is not None:
            setattr(btn_wgt, 'not_all_list', btndef['not_all_list'])

        # add the event handler method
        btn_wgt.bind('<Button-1>', self._toggle_changes_event_handler)

        # TODO: only the sections that should have been removed to default on (from the 'defect_instance')
        # default to all toggles on
        btndef['params']['variable'].set(btndef['params']['onvalue'])

        # add it to the wgts dict
        return btn_wgt

    def _get_toggle_definitions(self, num_of_buttons=3):
        """Get the dictionary defining the 'all' and 'left', 'center', and 'right' sides' toggle buttons' attributes.

        :return: dict, the definition dictionary.
        """
        # define the sides buttons
        number_of_buttons_to_definitions_lists = {1: [], 2: ['left', 'right'], 3: ['left', 'center', 'right'],
                                                  4: ['left', 'left_center', 'right_center', 'right'],
                                                  5: ['left', 'left_center', 'center', 'right_center', 'right']}
        self.not_all_list = number_of_buttons_to_definitions_lists[num_of_buttons]
        side_button_text = {'left': 'Operator Side\n', 'left_center': 'Operator Side of Center\n',
                            'center': 'Center of Foam\n', 'right_center': 'Foamline Side of Center\n',
                            'right': 'Foamline Side\n'}
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
        return button_def_dict

    def _destroy_toggle_panel(self):
        """Hide the current button frame for this defect_instance panel."""
        # self.btn_frame.destroy()
        self.btn_frame.grid()

    def _change_toggle_count(self):
        """Change the number of toggle-buttons on the the foam removed toggles frame."""
        self._destroy_toggle_panel()
        self._add_foam_removed_toggle_selectors(self)

    def _toggle_changes_event_handler(self, event):
        """Handle the toggle button being changed with regard to its designation and the state of the other toggles.

        If the 'all' button is turned on or off set the 'sides' to the same.
        If all of the 'sides' are turned on set the 'all' to the same.
        If any of the 'sides' are turned off, turn off the 'all'.

        :param event: tkinter.Event, for the toggle button being pressed.
        """
        msg_id, now_on, side = self._get_event_info(event)

        # this is just for development
        dbg_vars = (event, event.widget.msg_id, event.widget.side,
                    event.widget.state_var.get(), event.widget.state(), f'new {now_on}')
        lg.debug('_toggle_changes_event_handler - %s, ' * len(dbg_vars), *dbg_vars)

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
        """Get the side, new state, and defect_instance id from the widget calling the event.

        :param event: tkinter.Event, the button press event.
        :return: tuple, of the info.
        """
        msg_id = event.widget.msg_id  # the custom id attribute, used to track which defect_instance this relates to
        try:
            side = event.widget.side  # left, right, center, all
            now_on = 'selected' not in event.widget.state()  # whether the toggle is turning on or off; was selected
            # -> off
        except AttributeError:
            # TODO: make this function better
            # it must have been the send button
            return msg_id

        return msg_id, now_on, side

    def button_command(self):
        pass

    def add_toggle(self, button, side):
        """add a state tracker on the button, a side property, and add a side state tracker to the defect_instance frame

        :param button: tkinter.ttk.CheckButton
        :param side: str, the 'side' for the button
        """
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

# if __name__ == '__main__':
#     from fresk.models.defect import DefectModel
#     from fresk.flask_app import start_flask_app
#     from threading import Thread
#     from collections import deque
#     import time
#
#     root = tk.Tk()
#     in_out_q = deque()
#     flask_thread = Thread(target=start_flask_app, args=(in_out_q, in_out_q))
#     flask_thread.start()
#     while not len(in_out_q):
#         lg.debug(f'waiting for flask {in_out_q}')
#         time.sleep(1)
#     app = in_out_q.pop()['flask_app']
#     with app.app_context():
#         dd = DefectModel.new_defect()
#     MessagePanel(root, dd, 0)
if __name__ == '__main__':
    from dev_common import style_component


    class DummyDefect(object):
        """For testing the attributes window."""

        def __init__(self):
            self.id = 99
            self.defect_type = 'puckering'
            self.rolls_of_product_post_slit = 3
            self.length_of_defect_meters = 1.0
            self.record_creation_source = 'operator'


    root = tk.Tk()
    style_component(root, '..')
    defect1 = DummyDefect()
    lg.debug(defect1.__dict__)

    for frame in ((DefectTypePanel, 'type'), (LengthSetFrames, 'length'), (NumberPrompt, 'number')):
        frm = frame[0](root, defect1)
        frm.grid()

    root.mainloop()
    print(defect1.__dict__)
