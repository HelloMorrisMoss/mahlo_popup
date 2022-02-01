import functools
import tkinter as tk
from tkinter import ttk

from dev_common import reasons, style_component
from log_setup import lg
from widgets.length_entry import UpDownButtonFrame


# TODO: rename this something better, like horizontal number selector
class NumberPrompt(tk.ttk.LabelFrame):
    """A ttk.LabelFrame prompting for a number between 1 and 5."""

    def __init__(self, parent, defect):
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



        self.value = tk.IntVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
        for btn in self._count_value_buttons:
            btn.config(style='')
        event.widget.config(style='Accent.TButton')
        self.defect.rolls_of_product_post_slit = int(event.widget['text'])


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

        self.rolls_count_selector = NumberPrompt(self, defect)
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
        self._last_set_lengths = []  # list of the field_name for the most recently changed in order
        self._internal_update_running = False
        # add the length set frames
        self._length_set_tuples = ('length_of_defect_meters', 'Length Removed'), \
                                  ('mahlo_start_length', 'Start Length'), \
                                  ('mahlo_end_length', 'End Length')

        self._length_set_frames = {}

        for col, (field_name, text) in enumerate(self._length_set_tuples):
            this_var = tk.StringVar()
            this_frame = UpDownButtonFrame(self, self.defect, tkvar=this_var, field_name=field_name,
                                           increment_values=[0.1, 1, 5, 10], text=text)
            this_frame.grid(row=0, column=col, rowspan=2, sticky='ns')
            this_var.trace_add('write', functools.partial(self._auto_fill_third_length, field_name))
            self._length_set_frames.update({field_name: {'frame': this_frame, 'StringVar': this_var}})

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


class HolderFrame(ttk.Frame):
    def __init__(self, parent, text, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._holder_label = ttk.Label(self, text=text)
        self._holder_label.grid()


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


if __name__ == '__main__':
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


    def show_win():
        def nothing():
            pass

        show_button.grid_remove()
        sda = SelectDefectAttributes(root, defect=defect1, on_destroy=nothing)
        sda.grid(row=0, column=0)
        # udbf = UpDownButtonFrame(nwin, defect=defect1)
        # udbf.grid(row=0, column=0)


    show_button = tk.Button(root, command=show_win)
    show_button.grid(row=0, column=0)
    show_button.focus_force()
    root.mainloop()
    print(defect1.__dict__)
