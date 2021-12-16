"""For development helpers, in their own module to avoid circular imports and keep things organized."""
import os
import tkinter as tk
from tkinter import ttk


def recurse_tk_structure(obj: tk.Widget, name='starting_level', indent=0, print_structure=True, apply_function=None,
                         apply_args=([], {})):
    """Recursively move down the nested tkinter objects by their 'children' attribute, printing the structure.

    :param apply_function:
    :param apply_args:
    :param function:
    :param obj: tkinter object.
    :param name: the 'key' from the next level up dict for this object.
    :param indent: how far to indent the print statement.
    """
    if print_structure:
        ind_space = ' ' * indent
        print(f'{ind_space}{name} - {obj}: ')

    if apply_function:
        apply_function(obj, *apply_args[0], **apply_args[1])

    try:
        for name, kid in obj.children.items():
            recurse_tk_structure(kid, name, indent + 4)
    except AttributeError:
        print(f'{ind_space}leaf - end')


def hover_enter_factory(this_widget):
    """Bind a mouse-hover function to a tkinter widget to display information when hovered.

    :param this_widget: a tkinter widget.
    """
    this_widget = this_widget
    winfo = this_widget.grid_info()

    def set_loc_label(event, this_widget):
        event_widget = event.widget
        print(this_widget, event_widget, winfo)

    import functools

    this_fn = functools.partial(set_loc_label, this_widget=this_widget)

    this_widget.bind("<Enter>", this_fn)


def recurse_hover(wgt, indent=0):
    """Recursively move down the nested tk objects by their 'custom' .wgt dict items adding a mouse-over function.

    :param wgt: tkinter.Widget, highest level tkinter widget to set hover (can be the 'root' tk.Tk).
    :param indent: int, spaces to indent
    """

    hover_enter_factory(wgt)
    for child in wgt.winfo_children():
        recurse_hover(child, indent=indent + 4)


def to_the_front(self):
    """Move the window to the front.

    :param self: tkinter.widget, component with the root window as its .root attribute.
    """
    raise_above_all(self.root)


def raise_above_all(window):
    """Move the window to the front, by setting always on top than turning it off again.

    :param window: tkinter.widget, component with the root window as its .root attribute.
    """
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)


def add_show_messages_button(parent_container, current_messages_count, command):
    # the messages received button that shows when the window doesn't have focus
    # parent_container.columnconfigure(0, weight=1)  # to make the button able to fill the width
    # parent_container.rowconfigure(0, weight=1)  # to make the button able to fill the height
    number_of_messages_button = tk.ttk.Button(parent_container, text=str(current_messages_count),
                                              style='Accent.TButton')
    number_of_messages_button.bind('<Button-1>', command)  # bind the 'show messages' fn
    parent_container.columnconfigure(0, weight=1)  # to make the button able to fill the width
    parent_container.rowconfigure(0, weight=1)  # to make the button able to fill the height
    return number_of_messages_button


class StrCol(tk.StringVar):
    """A tk.StringVar that takes a flask-sqlalchemy Model and a bool column name and sets it with the str"""

    def __init__(self, defect, column):
        super().__init__()
        self.defect_interface = defect
        self.column = column

    def set(self, value):
        if 'not' not in value.lower():
            new_bool = True
        else:
            new_bool = False
        setattr(self.defect_interface, self.column, new_bool)
        super().set(value)


reasons = (
    'belt_marks', 'bursting', 'contamination', 'curling', 'delamination', 'lost_edge', 'puckering',
    'shrinkage',
    'thickness', 'wrinkles', 'other')


def style_component(component, path_override=''):
    """Add the styling for the component.

    :param component: tkinter.widget
    """
    component.tk.call("source", os.path.join(path_override, "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl"))
    component.tk.call("set_theme", "dark")
    component._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': 'Card.TFrame'}
