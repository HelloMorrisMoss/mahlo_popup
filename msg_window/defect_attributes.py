import tkinter as tk

from dev_common import reasons, style_component
from log_setup import lg


class LengthButton(tk.ttk.Button):
    def __init__(self, parent, length_var, direction_str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.length_var = length_var
        self.parent = parent
        if direction_str == 'up':
            self.increment_val = 1
        elif direction_str == 'down':
            self.increment_val = -1

        self.bind('<Button-1>', self.increment)

    def increment(self, *args):
        """Increase or decrease the variable.

        :param args: tuple, unused tkinter params.
        """
        self.length_var.set(str(int(float(self.length_var.get())) + self.increment_val))
        pass


class UpDownButtonFrame(tk.ttk.LabelFrame):
    """A frame with up and down buttons that increments a value displayed on a label."""
    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Length Removed')
        self.defect = defect
        self.length_var = tk.StringVar()
        self.length_var.set(str(defect.length_of_defect_meters))
        self.length_var.trace('w', self.update_length)
        self.length_label = tk.ttk.Label(self, text=self.length_var.get())
        self.length_label.grid(row=1, column=0)
        self.up_button = LengthButton(self, self.length_var, 'up', text='+')

        # what's up button? the button that makes the length go up, and down down
        self.up_button.grid(row=0, column=0, sticky='nsew')
        self.down_button = LengthButton(self, self.length_var, 'down', text='-')
        self.down_button.grid(row=2, column=0, sticky='nsew')

    def update_length(self, *args):
        """Update the label and defect value. TODO: pull the defect parts out of here, make this publish --> reusable.

        :param args: tuple, unused tkinter arguments.
        """
        new_val = self.length_var.get()
        self.length_label.config(text=new_val)
        self.defect.length_of_defect_meters = int(new_val)


class NumberPrompt(tk.ttk.LabelFrame):
    """Show a tk popup window prompting for a number between 1 and 5, returning that value when pressed."""

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

        add_ok_button(parent, self.parent)

        self.value = tk.IntVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
        for btn in self._count_value_buttons:
            btn.config(style='')
        event.widget.config(style='Accent.TButton')
        self.defect.rolls_of_product_post_slit = int(event.widget['text'])


def add_ok_button(parent, destroy_on_press=None):
    destroy_on_press = parent if destroy_on_press is None else destroy_on_press
    parent.ok_buton = tk.ttk.Button(parent, text='OK')

    def on_destroy(*args):
        parent.on_destroy()
        destroy_on_press.destroy()

    parent.ok_buton.bind('<Button-1>', on_destroy)
    parent.ok_buton.grid(row=1, column=6)


# class SelectDefectAttributes(tk.Toplevel):
#     def __init__(self, parent, defect, *args, **kwargs):
#         tk.Toplevel.__init__(self, parent, *args, **kwargs)
class SelectDefectAttributes(tk.ttk.LabelFrame):
    def __init__(self, parent, defect, on_destroy, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)  # this is required not super()
        self.parent = parent
        self.defect = defect
        self.on_destroy = on_destroy
        lg.debug('on destroy %s', on_destroy)

        self.defect_type_panel = DefectTypePanel(self, defect)
        self.defect_type_panel.grid(row=0, column=1)

        self.rolls_count_selector = NumberPrompt(self, defect)
        self.rolls_count_selector.grid(row=1, column=1)

        self.length_buttons = UpDownButtonFrame(self, defect)
        self.length_buttons.grid(row=0, column=0, rowspan=2, sticky='ns')

        self.value = tk.IntVar()


class DefectTypePanel(tk.ttk.LabelFrame):
    """Show a tk popup window prompting for a defect type, returning that value when pressed. Cancel as 'none'."""

    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Defect Type', *args, **kwargs)
        self.defect = defect
        row = 0
        col = 0

        reasons_and_cancel = reasons + ('cancel',)

        self._type_buttons = []

        for rn, reason in enumerate(reasons_and_cancel):
            button_label_text = reason  # if reason != 0 else 'Cancel'
            reason_button = tk.ttk.Button(self, text=button_label_text)
            reason_button.bind('<Button-1>', self.return_button_val)
            reason_button.grid(row=row, column=col, sticky='ew', padx=2, pady=2)
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
        for btn in self._type_buttons:
            btn.config(style='')
        event.widget.config(style='Accent.TButton')
        self.defect.defect_type = event.widget['text']


if __name__ == '__main__':
    class DummyDefect(object):
        """For testing the attributes window."""

        def __init__(self):
            self.defect_type = ''
            self.rolls_of_product_post_slit = 3
            self.length_of_defect_meters = 1


    root = tk.Tk()
    style_component(root, '..')
    defect1 = DummyDefect()
    lg.debug(defect1.__dict__)


    def show_win():
        def nothing():
            pass

        return SelectDefectAttributes(root, defect=defect1, on_destroy=nothing)


    show_button = tk.Button(root, command=show_win)
    show_button.pack()
    show_button.focus_force()
    root.mainloop()
    print(defect1.__dict__)
