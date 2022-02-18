"""Contains panels and widgets for displaying and changing the attributes of a defect."""

import functools
import tkinter as tk
from tkinter import ttk

from dev_common import reasons, style_component
from log_setup import lg
from widgets.length_entry import UpDownButtonFrame
from widgets.numpad_entry import NumpadEntry


class HorizontalNumButtonSelector(tk.ttk.LabelFrame):
    """A ttk.LabelFrame prompting for a number between 1 and 5."""

    def __init__(self, parent, defect, variable=None):
        super().__init__(parent, text='Number of finished good rolls', style='Card.TFrame')
        self.parent = parent
        self.row = 0
        self.defect = defect
        self._style = tk.ttk.Style()
        self._style.configure('TButton', background='black')

        # for iterating over
        self._count_value_buttons = []

        for col in range(1, 6):
            button_label_text = str(col)
            num_button = tk.ttk.Button(self, text=button_label_text)
            num_button.bind('<Button-1>', self.return_button_val)
            num_button.grid(row=self.row, column=col, padx=2, pady=2)
            self._count_value_buttons.append(num_button)
            if self.defect.rolls_of_product_post_slit == col:
                num_button.config(style='Accent.TButton')

        self.value = variable

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
        for btn in self._count_value_buttons:
            btn.config(style='')
        event.widget.config(style='Accent.TButton')
        intval = int(event.widget['text'])
        self.defect.rolls_of_product_post_slit = intval
        self.value.set(intval)


class SelectDefectAttributes(tk.ttk.Frame):
    """A ttk.LabelFrame with options to change the defect type, length removed, and number of rolls after slitting."""

    # TODO: need to be able to set the lot#, destroy multiple rolls

    def __init__(self, parent, defect, on_destroy, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)  # this is required not super()
        self.parent = parent
        self.defect = defect
        self.on_destroy = on_destroy
        self._not_length_wdigets = []
        lg.debug('on destroy %s', on_destroy)

        self.defect_type_panel = DefectTypePanel(self, defect)
        self.defect_type_panel.grid(row=0, column=10)
        self._not_length_wdigets.append(self.defect_type_panel)

        self.rolls_count_selector = HorizontalNumButtonSelector(self, defect)
        self.rolls_count_selector.grid(row=1, column=10)
        self._not_length_wdigets.append(self.rolls_count_selector)

        self._length_set_updown_frames = LengthSetFrames(self, defect)
        self._length_set_updown_frames.grid(row=0, column=0, sticky='nesw')
        self._show_all_set_lengths()

        self._ok_button = ttk.Button(self, text='OK', command=self._confirm_all_lengths)
        self._ok_button.grid(row=1, column=11)
        self._ok_button.grid_remove()
        self.bind('<<LengthsSet>>', self._hide_all_set_lengths)

        self.value = tk.IntVar()

    def _confirm_all_lengths(self, event=None):
        self.grid_remove()
        self.parent.event_generate('<<AttributesOK>>')

    def _show_all_set_lengths(self):
        lg.debug('hiding type and roll, showing lengths')
        self._length_set_updown_frames._show()
        self.defect_type_panel.grid_remove()
        self.rolls_count_selector.grid_remove()

    def _hide_all_set_lengths(self, event=None):
        lg.debug('showing type and roll, hiding lengths')
        self._length_set_updown_frames._hide()
        self.defect_type_panel.grid()
        self.rolls_count_selector.grid()
        self._ok_button.grid()


# TODO: when two of these have been changed, set the third
class LengthSetFrames(ttk.Frame):
    def __init__(self, parent, ls_defect, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.defect = ls_defect
        self.parent = parent
        self._internal_update_running = False
        self.toggle_auto_fill_lengths = tk.IntVar()
        self.toggle_auto_fill_lengths.set(True)
        # add the length set frames
        self._length_set_tuples = ('length_of_defect_meters', 'Length Removed'), \
                                  ('mahlo_start_length', 'Start Length'), \
                                  ('mahlo_end_length', 'End Length')
        self._last_set_lengths = ['mahlo_start_length',
                                  'mahlo_end_length']  # list of the field_name for the most recently changed in order

        self._length_set_frames = {}

        for col, (field_name, text) in enumerate(self._length_set_tuples):
            this_var = tk.StringVar()
            this_var.set(str(getattr(self.defect, field_name)))
            this_frame = UpDownButtonFrame(self, self.defect, variable=this_var, field_name=field_name,
                                           increment_values=[0.1, 1, 5, 10], text=text)
            this_frame.grid(row=0, column=col, rowspan=2, sticky='ns')
            this_var.trace_add('write', functools.partial(self._auto_fill_third_length, field_name))
            self._length_set_frames.update({field_name: {'frame': this_frame, 'StringVar': this_var}})

        self.toggle_auto_button = ttk.Checkbutton(self, text='autofill', variable=self.toggle_auto_fill_lengths)
        self.toggle_auto_button.grid(row=0, column=col + 1)

        # self._all_length_set_button = ttk.Button(self, text='all set',
        #                                          command=lambda: self.parent.event_generate('<<LengthsSet>>'))
        # self._all_length_set_button.grid(row=0, column=3, rowspan=2)

    def _auto_fill_third_length(self, this_length, *args, **kwargs):
        # if the value was just updated by this, don't run again from the update
        if self._internal_update_running:
            self._internal_update_running = False
            return
        else:
            self._internal_update_running = True

        # if there are no previous length changes, save this one and do nothing else
        if not self._last_set_lengths:
            self._internal_update_running = False
            self._last_set_lengths.append(this_length)
            return

        # if this is not the same length changed as last time, add it to the list
        if this_length != self._last_set_lengths[-1]:
            self._last_set_lengths.append(this_length)

        # if there are more than 2, remove the oldest
        lg.debug('current _last_set_lengths %s', self._last_set_lengths)
        if len(self._last_set_lengths) > 2:
            self._last_set_lengths = self._last_set_lengths[-2:]  # get rid of extras

            # case 1: start and end lengths -> subtract end from start, set total to that
            # case 2: start and total - > add start and total, set end to that
            # case 3: end and total -> subtract end from total, set start to that
            # if they changed report in the middle of this then anything with the end could be weird

            # need the field_name from tuples that isn't in last set lengths
        if self.toggle_auto_fill_lengths.get():
            def which_is_missing():
                for field_name, _ in self._length_set_tuples:
                    if field_name not in self._last_set_lengths:
                        return field_name

            from operator import add, sub

            missing_value_string = which_is_missing()

            if missing_value_string == 'length_of_defect_meters':
                field_names = 'mahlo_end_length', 'mahlo_start_length'
                self.reconcile_values(*field_names, sub, missing_value_string)
            elif missing_value_string == 'mahlo_end_length':
                field_names = 'mahlo_start_length', 'length_of_defect_meters'
                self.reconcile_values(*field_names, add, missing_value_string)
            elif missing_value_string == 'mahlo_start_length':
                field_names = 'mahlo_end_length', 'length_of_defect_meters'
                self.reconcile_values(*field_names, sub, missing_value_string)

    def reconcile_values(self, field_name1, field_name2, operation, missing_field_name):
        _value1 = float(self._length_set_frames[field_name1]['StringVar'].get())
        _value2 = float(self._length_set_frames[field_name2]['StringVar'].get())
        new_value = str(round(operation(_value1, _value2), 2))
        self._length_set_frames[missing_field_name]['StringVar'].set(new_value)

    def _hide(self):
        self.grid_remove()

    def _show(self):
        self.grid()


class DefectTypePanel(tk.ttk.LabelFrame):
    """A ttk.LabelFrame prompting for a defect type."""

    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Defect Type', *args, **kwargs)
        self.parent = parent
        self.defect = defect
        row = 0
        col = 0

        self._type_buttons = []

        # add the reason for removal buttons
        for rn, reason in enumerate(reasons):
            button_label_text = reason  # if reason != 0 else 'Cancel'
            reason_button = tk.ttk.Button(self, text=button_label_text)
            reason_button.bind('<Button-1>', self.return_button_val)
            reason_button.grid(row=row, column=col, sticky='ew', padx=2, pady=2)
            if self.defect.defect_type == reason:
                reason_button.config(style='Accent.TButton')
            col += 1
            if col > 5:
                row += 1
                col = 0

            self._type_buttons.append(reason_button)

        self.value = tk.StringVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """

        # clear any 'selected' buttons
        for btn in self._type_buttons:
            btn.config(style='')
        # accent this button
        event.widget.config(style='Accent.TButton')
        self.defect.defect_type = event.widget['text']


class LotNumberEntry(ttk.Labelframe):
    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Lot #', *args, **kwargs)
        self.parent = parent
        self.defect = defect
        self.lot_number_var = tk.StringVar()
        self.lot_number_var.set(defect.source_lot_number)
        self.lot_number_var.trace_add('write', self.update_lot_number)

        self._display_var = tk.StringVar()
        self._display_label = ttk.Label(self, textvariable=self._display_var)
        self._display_label.grid(row=0, column=0)
        self._display_format = '{value:_}'

        self.numpad_entry = NumpadEntry(self, textvariable=self.lot_number_var)
        self.numpad_entry.grid(row=1, column=0)

    def _update_display(self):
        new_val = self.lot_number_var.get()
        if new_val:
            display_string = ''
            display_pieces = (4, 7, 10)
            for dp in display_pieces:
                if len(new_val) >= dp:
                    new_val = new_val[:dp] + '_' + new_val[dp:]
        self._display_var.set(new_val)

    def update_lot_number(self, *args):
        lg.debug(f'{args=}')
        self.defect.source_lot_number = self.lot_number_var.get()
        self._update_display()


if __name__ == '__main__':
    class DummyDefect(object):
        """For testing the attributes window."""

        def __init__(self):
            self.id = 99
            self.defect_type = 'puckering'
            self.rolls_of_product_post_slit = 3
            self.length_of_defect_meters = 1.0
            self.record_creation_source = 'operator'
            self.source_lot_number = ''
            self.mahlo_start_length = 12.34
            self.mahlo_end_length = 43.21


    root = tk.Tk()
    style_component(root, '..')
    defect1 = DummyDefect()
    lg.debug(defect1.__dict__)

    for frame in (
            (LotNumberEntry, 'lot'), (DefectTypePanel, 'type'), (LengthSetFrames, 'length'),
            (HorizontalNumButtonSelector, 'number')):
        frm = frame[0](root, defect1)
        frm.grid()

    root.mainloop()
    print(defect1.__dict__)
