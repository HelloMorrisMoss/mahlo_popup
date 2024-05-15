"""For development helpers, in their own module to avoid circular imports and keep things organized."""
import datetime
import logging
import os
import subprocess
import sys
import tkinter
import tkinter as tk
from tkinter import ttk
from typing import Type, TypeVar, Union

from log_and_alert.log_setup import lg
from log_and_alert.program_restart_records import get_last_restart_record
from untracked_config.lam_num import LAM_NUM


def recurse_tk_structure(obj: tk.Widget, name='starting_level', indent=0, print_structure: callable = print,
                         apply_function=None, apply_args: tuple = ([], {})):
    """Recursively move down the nested tkinter objects by their 'children' attribute, acting on all of them.

    By default will print the structure to the console.

    :param obj: Type[tkinter.Misc], the top of the tk object tree to start the recursion. A window or widget.
    :param name: the 'key' from the next level up dict for this object.
    :param indent: how far to indent the print statement.
    :param print_structure: callable, default is builtins.print, how to print or log the structure. False to turn off.
    :param apply_function: callable, (optional) a function to apply to the object.
    :param apply_args: tuple, (optional) contains the args and kwargs to pass to the apply_function. Ex: ([], {})
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


def hover_enter_factory(this_widget: Type[tkinter.Widget]):
    """Bind a mouse-hover function to a tkinter widget to display information when hovered.

    :param this_widget: a tkinter widget.
    """

    # TODO: double check the late binding stuff in here; I think this built to check for late binding
    this_widget = this_widget  # this might have been here to protect against late binding, still needed?
    winfo = this_widget.grid_info()

    def set_loc_label(event, this_widget):
        # I think this was checking whether late binding had caused a mismatch in widgets
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
        with self.defect_interface.session() as session:
            setattr(self.defect_interface, self.column, new_bool)
            self.defect_interface.session.remove()
        super().set(value)


class NumStrVar(tk.StringVar):
    """A tk.StringVar that holds a positive 'float' value and attempts to set to a negative value can be suscrbied."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alt_min_var = None
        self._alt_max_var = None
        self._negative_subscribers = {}
        self._alt_min_subscribers = {}
        self._previous_values = []
        self._dynamic_min = None
        self._dynamic_max = None
        self._nsv_name_str = ''

    def set_nsv_name(self, the_name: str):
        self._nsv_name_str = the_name

    def subscribe_to_negatives(self, subscriber: object, subscription_callable: callable):
        sub_id = id(subscriber)
        if sub_id not in self._negative_subscribers.keys():
            self._negative_subscribers[sub_id] = subscription_callable

    def publish_negative_attempt(self):
        for sub, callme in self._negative_subscribers.items():
            callme()

    def subscribe_to_alt_min(self, subscriber: object, subscription_callable: callable):
        if subscriber not in self._alt_min_subscribers.index(subscriber):
            self._alt_min_subscribers[subscriber] = subscription_callable

    def publish_alt_min(self):
        for sub, callme in self._alt_min_subscribers:
            callme()

    def set_alternative_minimum_variable(self, alt_min):
        self._alt_min_var = alt_min

    def set_alternative_maximum_variable(self, alt_max):
        self._alt_max_var = alt_max

    # def set_dynamic_limits(self, dynamic_max, dynamic_min):
    #     self._dynamic_min = dynamic_min
    #     self._dynamic_max = dynamic_max
    #
    # def get_dynamic_range(self):
    #     return self._dynamic_min.get(), self._dynamic_max.get()
    #
    # def dynamic_limits_are_set(self):
    #     return self._dynamic_min is not None and self._dynamic_max is not None
    #
    # def check_within_dynamic_range(self, new_value):
    #     if self.dynamic_limits_are_set():
    #         dmin, dmax = self.get_dynamic_range()
    #         return dmin <= new_value <= dmax
    #     else:
    #         return True

    def set(self, new_value):
        try:
            new_float = float(new_value)

            if new_float >= 0:
                within_limits = self.check_alt_limits(new_float)
                if within_limits:
                    super().set(str(new_value))
                    self._previous_values.append(new_value)
                    lg.debug('%s: new value set %s and added to previous values: %s',
                             self._nsv_name_str, new_value, self._previous_values)
            else:
                self.publish_negative_attempt()
        except ValueError:
            pass  # this is going to happen regularly and isn't a problem

    def revert_to_previous_value(self):
        current_value = self._previous_values.pop()
        lg.debug('Reverting to previous value: %s from: %s', self._previous_values, current_value)
        self.set(self._previous_values[-1])

    def check_alt_limits(self, new_float):
        # if not self.check_within_dynamic_range(new_float):
        #     return False
        if isinstance(self._alt_min_var, NumStrVar):
            alt_min = self._alt_min_var.get()
        else:
            alt_min = 0.0

        if new_float < alt_min:
            return False

        if isinstance(self._alt_max_var, NumStrVar):
            alt_max = self._alt_max_var.get()
            if new_float > alt_max:
                return False
        return True

    def get(self):
        try:
            return_value = float(super().get())
            lg.debug('value returned %s', return_value)
            return return_value
        except ValueError:
            pass  # many won't be convertable


reasons = (
    'belt_marks', 'bursting', 'contamination', 'curling', 'delamination', 'lost_edge', 'puckering',
    'shrinkage',
    'thickness', 'wrinkles', 'recipe_change', 'other')


def style_component(component, path_override=''):
    """Add the styling for the component.

    :param component: tkinter.widget
    """
    component.tk.call("source", os.path.join(path_override, "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl"))
    component.tk.call("set_theme", "dark")
    component._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': 'Card.TFrame'}


# for type hinting for either Toplevel or subclasses
tkToplevel = TypeVar('tkToplevel', bound=tkinter.Toplevel)


def window_topmost(window: tkToplevel, set_to=True, lift=True):
    """Set a tkinter window to remain on top of other windows when losing focus to them and lift to the top.

    :param window: tkinter.TopLevel, the window to work on.
    :param set_to: bool, whether to set to stay on top or not to stay on top, default=True.
    :param lift: bool, whether to lif tthe window above other windows.
    """

    window.attributes('-topmost', set_to)
    if lift:
        window.lift()


def dt_to_shift(dtime: datetime.datetime):
    """Convert a datetime.datetime to the shift that it would correspond to.

    :param dtime: datetime.datetime
    :return: int, the shift
    """

    now = dtime
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if seconds_since_midnight < 26_100:
        return 3
    elif seconds_since_midnight < 54_900:
        return 1
    elif seconds_since_midnight < 83_700:
        return 2
    else:
        return 3


def touch(file_path):
    """Create an empty file at the file path."""

    with open(file_path, 'w') as pf:
        pf.write('')


def blank_up(file_path, after_backup_function=touch):
    """Backup the file with a timestamp and replace with a blank file."""

    import time

    timestr = time.strftime("%Y%m%d-%H%M%S")
    fp, ext = os.path.splitext(file_path)
    new_fp = f'{fp}_BACKUP_{timestr}{ext}'
    os.rename(file_path, new_fp)
    lg.info('Backing up last_position.txt to %s', new_fp)
    touch(file_path)


def restart_program(lg: logging.Logger = None, source: any = None):
    """Restarts the popup and server. Optionally logs the restart and source.

    :param lg: logging.Logger, default None, a logger to use to record the restart.
    :param source: any, default None, a source to
    """

    try:
        if lg:
            lg.info('Restarting program.%s%s', 'Source: ' if source else '', source)
    except Exception as uhe:
        lg.info('Restarting program. Provided source could not be parsed: %s', uhe)
    finally:
        restart_arguments = [sys.executable, sys.executable, *sys.argv]
        os.execl(*restart_arguments)


def exception_one_line(exception_obj):
    """Get the exception traceback text as a one line string. New lines are replaces with escaped '\\n'.

    :param exception_obj: builtins.Exception, the exception.
    :return: str, the message string.
    """
    from traceback import format_exception
    return ''.join(format_exception(type(exception_obj), exception_obj, exception_obj.__traceback__)
                   ).replace('\n', '\\n')


def get_email_body_context(run_popup, run_server, on_dev_node, hostname) -> str:
    """Get a string containing contextual information about this program being run.

        :param run_popup: bool, whether the program should try to run the popup GUI.
        :param run_server: bool, whether the program should try to run the API/web server.
        :param on_dev_node: bool, whether the system where the program is running is considered a development node.
        :param hostname: str, the name of the host system where the program is running.
        :return: str

    """

    # todo: add a untracked_config/last_shutdown.(json,txt?) that contains the timestamp and shutdown reason
    #  (restart button, escape key, etc.) and include that information in the information below if present

    email_body_context = f'''Exception context:
        {LAM_NUM=}
        {run_popup=}
        {run_server=}
        {on_dev_node=}
        {hostname=}
        app_start_time={datetime.datetime.now()}
        current_user={os.getlogin()}
        system_boot_time={get_boot_time_str()}
        last_restart={get_last_restart_record()}
        '''.strip()

    try:
        import git

        head = git.Repo(search_parent_directories=True).head
        email_body_context += (f'''
        git_commit_ts={str(head.object.authored_datetime)}
        git_hash={head.object.hexsha}''')

    except ImportError:
        lg.warning('GitPython is not installed. Commit info will not be included in e-mail body context.')

    return email_body_context


def get_boot_time_str(format: str = None) -> str:
    """Get the boot time as a string.

    :param format: str, the datetime.datetime format string to use. Defaults to ISO format.

    :return: str, the datetime.datetime as a formatted string.
    """
    return_value = ''
    try:
        windows_boot_time = get_windows_boot_time()
        if format:
            return_value = windows_boot_time.strftime(format)
        else:
            return_value = windows_boot_time.isoformat()
    except Exception as uhe:
        lg.warning(uhe)
        return_value = exception_one_line(uhe)

    return return_value


def get_windows_boot_time() -> Union[datetime.datetime, None]:
    """Get the Windows boot time as a datetime.datetime object.

    :return: datetime.datetime, the Windows boot time, or None if it cannot be retrieved.

    """
    # # this works but it has a small lag as powershell starts up; doesn't work on the old Mahlo HMIs (old powershell)
    # datetime.datetime.strptime(subprocess.check_output(['powershell',
    # '(gcim Win32_OperatingSystem).LastBootUpTime']).strip().decode('UTF-8'), '%A, %B %d, %Y %I:%M:%S %p')

    command = "net stats workstation"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output, error = process.communicate()
    if process.returncode == 0:
        return datetime.datetime.strptime(output[output.index('since ') + 6: output.index('\n\n\n  Bytes')],
                                          '%m/%d/%Y %I:%M:%S %p')
    else:
        return None
