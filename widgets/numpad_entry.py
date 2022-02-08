"""Contains a tk.ttk.Entry that will spawn a number pad for entering and changing the value."""

import tkinter as tk
import tkinter.ttk
from tkinter import ttk


class NumpadEntry(ttk.Entry):
    """A tkinter.ttk.Entry that, when double_clicked, will show a number pad to edit the value."""

    def __init__(self, parent, textvariable: tk.StringVar = None, *args, **kwargs):
        if textvariable is None:
            kwargs['textvariable'] = tk.StringVar()
        else:
            kwargs['textvariable'] = textvariable
        super().__init__(parent, *args, **kwargs)
        self.textvariable = kwargs['textvariable']
        self.parent = parent
        self.bind('<Button-1>', self._quick_clicking)
        self._quick_clicks = 0
        self._previous_value = self.get()  # the last value
        self.previous_values = [self._previous_value]  # all previous values (for undo)
        self._last_button_pressed = 'None'
        self.textvariable.trace_add('write', self._add_to_undo_list)
        self._undoing = False

    def _add_to_undo_list(self, *args):
        if not self._undoing:
            new_value = self.get()
            self.previous_values.append(new_value)
            self._previous_value = new_value

    def undo(self, *args):
        self._undoing = True
        while self.previous_values:
            undoed_value = self.previous_values.pop()
            if undoed_value != self._previous_value:
                self.textvariable.set(undoed_value)
                self._previous_value = undoed_value
                self.icursor(tk.END)
                break
        self._undoing = False

    def numpad_closed(self, event):
        """If there are no entered numbers, but there had been before, clear the numbers."""
        self.winfo_toplevel().focus_force()
        if self.get() == '' and self._previous_value != '':
            self.insert(0, self._previous_value)

    def _quick_clicking(self, event=None):
        """Count the recent repeated and rapid clicks on the _entry, if it was double_clicked open the number pad.

        :param event: tkinter.Event
        """
        if self._quick_clicks == 1:
            self._reset_quick_clicks()
            self.show_numpad()
        else:
            self._quick_clicks += 1

            def unchanged_quick_clicks():
                print('reset quick')
                if self._quick_clicks == getattr(self, '_quick_clicks'):
                    self._reset_quick_clicks()

            self.after(500, unchanged_quick_clicks)

    def _reset_quick_clicks(self):
        """Set the count of quick clicks to 0."""
        self._quick_clicks = 0

    def show_numpad(self):
        """Show a new window with a number pad to edit the _entry's value."""

        # save and clear the current value
        self._previous_value = self.get()
        # self.delete(0, tk.END)

        np = NumberPad(self)
        np.place(in_=self, relx=0, rely=1)
        self.after(10, lambda: self.selection_clear())


class NumberPad(tk.ttk.Frame):
    """A number pad window that edits the passed Entry widget's value."""

    def __init__(self, entry: NumpadEntry, prompt=None, **kwargs):
        super().__init__(entry.winfo_toplevel())
        self._button_dict = self.add_buttons()
        self._entry = entry
        self._original_value = self._entry.get()

        # this works but limits the reusability
        self.winfo_toplevel().bind_all("<Button-1>", self.auto_close)  # close the number pad when losing focus

    def add_buttons(self):
        """Add the buttons to the number pad.

        :return: dict, a dictionary of {'label': ttk.Button, ...}
        """
        button_labels = ['7', '8', '9',
                         '4', '5', '6',
                         '1', '2', '3',
                         '.', '0', 'backspace',
                         u'🡸', 'OK', u'🡺',
                         'undo', 'revert', 'clear',
                         'today']

        buttons_dict = {}
        padx = 1
        pady = padx

        num_cols = 3
        for row, column, label in [((i // num_cols), (i % num_cols), item) for i, item in enumerate(button_labels)]:
            command = lambda event, lambel=label: self.click(lambel)
            btn = ttk.Button(self, text=label, takefocus=False)
            btn.bind('<Button-1>', command)
            btn.grid(row=row, column=column, padx=padx, pady=pady)
            buttons_dict[label] = btn

        return buttons_dict

    def click(self, label):
        """Edit the _entry value.

        :param label:
        """
        current_cursor_index = self._entry.index(tk.INSERT)
        if label == 'backspace':
            # todo: if text is selected, delete it
            self._entry.delete(current_cursor_index - 1, current_cursor_index)
        elif label == 'OK':
            self.close_numpad()
        elif label == u'🡸':
            # todo: if text is selected, unselect when using arrow keys
            self._entry.icursor(current_cursor_index - 1)
        elif label == u'🡺':
            self._entry.icursor(current_cursor_index + 1)
        elif label == 'clear':
            self.clear()
        elif label == 'revert':
            self.revert()
        elif label == 'undo':
            self._entry.undo()
        elif label == 'today':
            import datetime
            datetime.datetime.today()
            self.replace_all(datetime.datetime.today().isoformat()[:10].replace('-', ''))
        else:
            # todo: if text is selected, replace selected text with label
            self._entry.insert(current_cursor_index, label)

    def revert(self):
        self.replace_all(self._original_value)
        self._entry.icursor(tk.END)

    def replace_all(self, new_value: str):
        """Replace the current value with something else.

        :param new_value: str
        """
        self.clear()
        self._entry.insert(0, new_value)

    def clear(self):
        """Set the value to an empty string."""

        self._entry.delete(0, tk.END)

    def auto_close(self, event):
        """If the window lost focus and does not have it, close the window.

        This guards against closing when pressing the buttons.

        :param event: tkinter.Event
        """

        # if it's not the numpad or descendants
        if not str(event.widget).startswith(str(self)):
            try:
                float(self._entry.textvariable.get())
            except ValueError:
                self.revert()
            self.close_numpad()

    def close_numpad(self):
        """Close the NumPad window."""

        # if nothing has been entered, but there was a value before, revert
        if self._entry.get() == '' and self._original_value != '':
            self.replace_all(self._original_value)
        self.winfo_toplevel().focus_force()
        self._entry.focus_force()
        self.winfo_toplevel().unbind_all("<Button-1>")
        self.destroy()


if __name__ == '__main__':
    # the most basic of testing
    root = tk.Tk()
    root.geometry('400x400+2500+200')  # place it on the second monitor for testing

    from dev_common import style_component

    style_component(root, r'..')
    txt_var = tk.StringVar()
    test_entry = NumpadEntry(root, textvariable=txt_var)
    test_entry.grid(row=0, column=0)

    txt_var2 = tk.StringVar()
    test_entry2 = NumpadEntry(root, textvariable=txt_var2)
    test_entry2.grid(row=0, column=1)
    # root.bind_all("<1>", lambda event: event.widget.focus_set())
    root.mainloop()
