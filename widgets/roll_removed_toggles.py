import tkinter
import tkinter as tk
from tkinter import ttk

from dev_common import StrCol
from log_setup import lg


class RollRemovedToggles(tk.Frame):
    def __init__(self, parent, defect_rrt, *args, **kwargs):
        self.defect_interface = defect_rrt
        super().__init__(parent, *args, **kwargs)

        self.pad = {'x': 2, 'y': 2}

        sides_to_defect_columns_dict = {'left': 'rem_l', 'left_center': 'rem_lc',
                                        'center': 'rem_c', 'right_center': 'rem_rc', 'right': 'rem_r'}

        self.removed_vars = {k: StrCol(self.defect_interface, col) for k, col in sides_to_defect_columns_dict.items()}
        self.removed_vars.update({'all': tk.StringVar()})
        self._add_foam_removed_toggle_selectors()

    def _add_foam_removed_toggle_selectors(self):
        """Add the toggle buttons frame to the parent frame.

        :param message: dict, the defect_instance dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """

        # TODO: move the 'change number of rolls selector' to be with the rolls removed
        # default to the guessed number
        # number_of_buttons = defect_interface['toggle_count_guess']
        number_of_buttons = self.defect_interface.rolls_of_product_post_slit

        self.toggle_button_def_dict = self._get_toggle_definitions(number_of_buttons)

        self._toggle_refs = {}

        # add them to the button frame
        for bnum, (btn, btndef) in enumerate(self.toggle_button_def_dict.items()):
            btndef['defect_interface'] = self.defect_interface
            self._toggle_refs[btn] = RemovedToggle(self, btn, btndef)
            self.add_toggle(self._toggle_refs[btn], btn)
            # add the event handler method
            self._toggle_refs[btn].bind('<Button-1>', self._toggle_changes_event_handler)  # TODO

        # add a line separator to make the all button stand out from the side buttons
        sep = ttk.Separator(self, orient='horizontal')
        sep_grid_dict = {'column': 0,
                         'row': 1,
                         'columnspan': 12,
                         'padx': self.pad['x'],
                         'pady': self.pad['y'],
                         'sticky': 'nesw'}
        sep.grid(**sep_grid_dict)

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
            self.removed_vars[side].set(set_str)

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
                                        'textvariable': self.removed_vars[side]},
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
                                              'textvariable': self.removed_vars['all']},
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

    def add_toggle(self, button, side):
        """add a state tracker on the button, a side property, and add a side state tracker to the defect_instance
        frame

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
                        side_val = self.removed_vars.get(iter_side).get()
                        sides_count += 'WAS removed' in side_val
                    lg.debug('iter_side %s, side_val %s, sides_count %s', iter_side, side_val, sides_count)

                if sides_count == len(self.not_all_list):
                    self._set_all_sides(('all',), True)


class RemovedToggle(ttk.Checkbutton):
    def __init__(self, parent: tkinter.Widget, btn_side, btndef, *args, **kwargs):
        """Add a toggle button to the frame using a definition dictionary.

        :param btn_frame: tkinter.Frame
        :param btn_side: str, the 'side' for the button.
        :param btndef: dict, definining parameters for the button.
        """

        text = btndef['params'].pop('text', None)
        self.defect_interface = btndef.pop('defect_interface')
        super().__init__(parent, text=text, style='Switch.TCheckbutton', *args, **kwargs)

        # add some custom attributes to use elsewhere, to keep track of which button is which
        setattr(self, 'state_var', btndef['params']['variable'])
        setattr(self, 'side', btn_side)
        setattr(self, 'msg_id', self.defect_interface.id)

        # if it is the 'all' button add the list of buttons to toggle
        if btndef.get('not_all_list') is not None:
            setattr(self, 'not_all_list', btndef['not_all_list'])

        # TODO: only the sections that should have been removed to default on (from the 'defect_instance')
        # default to all toggles on
        btndef['params']['variable'].set(btndef['params']['onvalue'])
        self.grid(**btndef['grid_params'])


if __name__ == '__main__':
    import dev_common


    class DummyDefect(object):
        """For testing the attributes window."""

        def __init__(self):
            self.id = 99
            self.defect_type = 'puckering'
            self.rolls_of_product_post_slit = 3
            self.length_of_defect_meters = 1.0
            self.record_creation_source = 'operator'


    root = tk.Tk()
    dev_common.style_component(root, '..')
    dd = DummyDefect()
    rr = RollRemovedToggles(root, defect_rrt=dd)
    rr.grid()
    root.mainloop()
