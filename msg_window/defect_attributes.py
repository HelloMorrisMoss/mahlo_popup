import tkinter as tk

from dev_common import reasons, style_component


class LengthButton(tk.ttk.Button):
    def __init__(self, parent, defect, direction_str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.defect = defect
        self.parent = parent
        if direction_str == 'up':
            self.increment = 1
        elif direction_str == 'down':
            self.increment = -1

        def increment(event=None):
            defect.length_of_defect_meters += self.increment

        self.bind('<Button-1>', increment)


class UpDownButtonFrame(tk.ttk.LabelFrame):
    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Length Removed')
        self.defect = defect
        self.length_var = tk.StringVar()
        self.length_var.set(str(defect.length_of_defect_meters))
        self.length_label = tk.ttk.Label(self, text=self.length_var.get())
        self.length_label.grid(row=1, column=0)

        # what's up button? the button that makes the length go up, and down down
        self.up_button = LengthButton(self, defect, 'up', text='+')
        self.up_button.grid(row=0, column=0, sticky='nsew')
        self.down_button = LengthButton(self, defect, 'down', text='-')
        self.down_button.grid(row=2, column=0, sticky='nsew')


class NumberPrompt(tk.ttk.LabelFrame):
    """Show a tk popup window prompting for a number between 1 and 5, returning that value when pressed."""

    def __init__(self, parent, defect):
        super().__init__(parent, text='Number of finished good rolls')
        row = 0
        self.defect = defect

        for col in range(1, 6):
            button_label_text = str(col)
            num_button = tk.ttk.Button(self, text=button_label_text)
            num_button.bind('<Button-1>', self.return_button_val)
            num_button.grid(row=row, column=col)
        self.value = tk.IntVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
        self.defect.rolls_of_product_post_slit = int(event.widget['text'])


class SelectDefectAttributes(tk.Toplevel):
    def __init__(self, parent, defect, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)  # this is required not super()
        self.defect = defect

        self.defect_type_panel = DefectTypePanel(self, defect)
        self.defect_type_panel.grid(row=0, column=1)

        self.rolls_count_selector = NumberPrompt(self, defect)
        self.rolls_count_selector.grid(row=1, column=1)

        self.length_buttons = UpDownButtonFrame(self, defect)
        self.length_buttons.grid(row=0, column=0, rowspan=2, sticky='ns')

        self.value = tk.IntVar()

    def show(self):
        self.wm_deiconify()
        self.focus_force()
        self.wait_window()
        return self.value.get()


class DefectTypePanel(tk.ttk.LabelFrame):
    """Show a tk popup window prompting for a defect type, returning that value when pressed. Cancel as 'none'."""

    def __init__(self, parent, defect, *args, **kwargs):
        super().__init__(parent, text='Defect Type', *args, **kwargs)
        self.defect = defect
        row = 0
        col = 0

        reasons_and_cancel = reasons + ('cancel',)

        for rn, reason in enumerate(reasons_and_cancel):
            button_label_text = reason if reason != 0 else 'Cancel'
            reason_button = tk.ttk.Button(self, text=button_label_text)
            reason_button.bind('<Button-1>', self.return_button_val)
            reason_button.grid(row=row, column=col)
            col += 1
            if col > 5:
                row += 1
                col = 0

        self.value = tk.StringVar()

    def return_button_val(self, event):
        """Set self.value to the widget['text'] value, or 0 if Cancel/anything without and int castable text is pressed.

        :param event: tkinter.Event
        """
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
    print(defect1.__dict__)


    def show_win():
        return SelectDefectAttributes(root, defect=defect1).show()


    show_button = tk.Button(root, command=show_win)
    show_button.pack()
    show_button.focus_force()
    root.mainloop()
    print(defect1.__dict__)
