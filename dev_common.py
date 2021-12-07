"""For development helpers, in their own module to avoid circular imports and keep things organized."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


def get_dummy_dict_by_ids(id_list=[1, 2, 3], oospec_len_meters=5.55,
                          template_str='At {timestamp}\nthere were {len_meters} meters oospec!'):
    return {'messages': [get_message_dict(mnum, msg_id, oospec_len_meters, template_str)
                         for mnum, msg_id in
                         enumerate(id_list)],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


def get_message_dict(mnum, msg_id, oospec_len_meters, template_str):
    return {'title': 'Out of spec!',
            'msg_txt': {'template': template_str,
                        'timestamp': datetime.now().isoformat(),
                        'length_in_meters': oospec_len_meters},
            'buttons': ['removed!', 'oops!'],
            'toggle_count_guess': mnum + 1,
            'msg_id': msg_id
            }


def get_dummy_dict(oospec_len_meters=5.55,
                   template_str='At {timestamp}\nthere were {len_meters} meters oospec!',
                   msg_count=5):
    return {'messages': [create_message_dict(mnum + 1, msg_id, oospec_len_meters, template_str)
                         for mnum, msg_id in
                         enumerate(('msg123', 'msg456', 'msg789', 'msg987', 'msg654'))],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


def create_message_dict(rolls_count_guess, msg_id, oospec_len_meters, template_str, window_title='Out of spec!'):
    return {'title': window_title,
            'msg_txt': {'template': template_str,
                        'timestamp': datetime.now().isoformat(),
                        'length_in_meters': oospec_len_meters},
            'buttons': ['removed!', 'oops!'],
            'toggle_count_guess': rolls_count_guess,
            'msg_id': msg_id
            }


def get_empty_dict():
    return {'messages': [],
            'main_win': {'title': 'Messages received!', 'timestamp_display_format': r'%I:%M %d-%b'}
            }


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
    raise_above_all(self.root)


def raise_above_all(window):
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
