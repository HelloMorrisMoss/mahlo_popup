"""Contains a frame containing an entry with a number pad for a numeric value and buttons to change the values."""

import tkinter as tk

from log_setup import lg
from widgets.numpad_entry import NumpadEntry


class UpDownButtonFrame(tk.ttk.LabelFrame):
    """A frame with up and down buttons that increments a value displayed on a label."""

    def __init__(self, parent, ud_defect, variable, *args, **kwargs):
        # keywords not intended for the LabelFrame
        incr_vals = kwargs.pop('increment_values', None)
        if not incr_vals:
            lg.debug('using default incr_vals')
            incr_vals = [1]
        self._field_name = kwargs.pop('field_name')

        super().__init__(parent, *args, **kwargs)
        self.defect = ud_defect
        self.length_var = variable
        self.length_var.trace('w', self.update_length)

        # todo: this could be its own class
        self.up_frame = tk.ttk.Frame(self)
        self.up_frame.grid(row=10, column=10, sticky='ew')
        # self.up_frame.grid_propagate(0)  # turns off auto sizing based on children, but currently shrinks to nothing
        self.down_frame = tk.ttk.Frame(self)
        self.down_frame.grid(row=70, column=10, sticky='ew')

        # add the increment buttons
        last_column = 10
        pad_val = 1

        for inc_val in incr_vals:
            # what's up button? the button that makes the length go up, and down down
            up_button = LengthButton(self.up_frame, self.length_var, 'up',
                                     text=f'{inc_val}', increment_magnitude=inc_val)

            up_button.grid(row=20, column=last_column, sticky='nsew', padx=pad_val, pady=pad_val)

            down_button = LengthButton(self.down_frame, self.length_var, 'down',
                                       text=f'{inc_val}', increment_magnitude=inc_val)
            down_button.grid(row=70, column=last_column, sticky='nsew', padx=pad_val, pady=pad_val)

            last_column += 10

        # the '+' label
        col_span = last_column
        self.up_label = tk.ttk.Label(self.up_frame, text='+')
        self.up_label.config(font=(None, 14))
        self.up_label.grid(row=10, column=10, columnspan=col_span)

        self._top_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
        self._top_divider.grid(row=5, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

        self._top_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
        self._top_divider.grid(row=30, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

        # label displaying the value
        self.length_entry = NumpadEntry(parent=self, textvariable=self.length_var, clicks=1, width=11, justify='center')
        self.length_entry.config(font=(None, 20))
        self.length_entry.grid(row=40, column=10, rowspan=2, columnspan=col_span, padx=(2, 2))

        self._bottom_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
        self._bottom_divider.grid(row=50, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

        # the '-' label
        self.down_label = tk.ttk.Label(self.down_frame, text='-')
        self.down_label.config(font=(None, 14))
        self.down_label.grid(row=80, column=10, columnspan=col_span)

    def update_length(self, *args):
        """Update the label and ud_defect value. TODO: pull the ud_defect parts out of here, make this publish -->
        reusable.

        :param args: tuple, unused tkinter arguments.
        """
        new_val = self.length_var.get()
        try:
            setattr(self.defect, self._field_name, float(new_val))
        except ValueError as ver:
            lg.debug('Not a valid float value %s - %s', new_val, ver)


class LengthButton(tk.ttk.Button):
    """A button to increase or decrease a tk.StringVar number value."""

    def __init__(self, parent, length_var, direction_str, *args, **kwargs):

        icr_mag = kwargs.pop('increment_magnitude', None)
        self.increment_magnitude = icr_mag if icr_mag else 1

        super().__init__(parent, *args, **kwargs)
        self.config(width=3)
        self.length_var = length_var
        self.parent = parent

        if direction_str == 'up':
            self.increment_val = self.increment_magnitude
        elif direction_str == 'down':
            self.increment_val = -1 * self.increment_magnitude

        self.bind('<Button-1>', self.increment)

    def increment(self, *args):
        """Increase or decrease the variable.

        :param args: tuple, unused tkinter params.
        """

        self.length_var.set(str(round(float(self.length_var.get()) + self.increment_val, 2)))
