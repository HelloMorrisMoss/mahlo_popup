"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""
import json
import tkinter
import tkinter as tk
from tkinter import ttk

from dev_common import add_show_messages_button, blank_up, exception_one_line, recurse_hover, recurse_tk_structure, \
    restart_program, style_component, window_topmost
from fresk.models.defect import DefectModel
from fresk.models.lam_operator import OperatorModel
from log_setup import lg
from msg_window.popup_frame import DefectMessageFrame
from scada_tag_query import TagHistoryConnector
from untracked_config.lam_num import LAM_NUM


class MainWindow(tk.Tk):
    """The main tkinter window that the defect_instance panels, controls, etc reside in."""

    def __init__(self, inbound_queue, outbound_queue, debugging=False, *args, **kwargs):
        """Initialize the main window.

        :type inbound_queue: collections.deque, inbound messages from flask
        :type outbound_queue: collections.deque, outbound messages from flask
        :type debugging: bool, whether to execute extra debugging code
        """
        super().__init__(*args, **kwargs)
        self.debugging = debugging
        # self.attributes('-toolwindow', True)  # don't show the min/max buttons on the title bar

        self.lam_num = LAM_NUM  # the laminator number
        self.title(f'Defect Removal Records - lam {self.lam_num}')

        # what to do when hiding
        self.current_form = None
        self._hide_option = tk.StringVar()
        self._hide_option.set('b')  # default to button
        self.message_button_geometry = '150x150'  # used for the message button and referenced by .show_hideables()
        self.full_window_geometry = '1150x450'
        self.full_sized()

        # whether to automatically hide/show the window
        self._auto_hide = tk.IntVar(value=True)
        self._auto_show = tk.IntVar(value=True)
        self._ghost_hide = tk.IntVar(value=True)
        self._ghost_fade = tk.IntVar(value=50)

        # communication with flask app
        if inbound_queue is not None:
            self.messages_from_flask = inbound_queue
        else:
            lg.warning('No inbound_queue')

        if outbound_queue is not None:
            self.messages_to_flask = outbound_queue
        else:
            lg.warning('No outbound_queue')

        # styling
        style_component(self)

        # frame padding
        self.pad = dict(x=5, y=3)

        grid_style_params = {'style_settings': {'pad': self.pad, '_wgt_styles': self._wgt_styles}}

        # list of components that need to 'hide' when the lam is running
        self.hideables = []

        # where the messages about defect appear with their toggles/save buttons
        self.popup_frame = DefectMessageFrame(self, lam_num=self.lam_num, **grid_style_params)
        self.popup_frame.grid(row=0, column=0, sticky='nesw')
        self.hideables.append(self.popup_frame)

        # the button that shows while inactive, displays the number of new defects
        self.number_of_messages_button = add_show_messages_button(self, 0, self.show_hideables)
        self.number_of_messages_button.grid(row=0, column=0, sticky='nesw')
        self.number_of_messages_button.grid_remove()
        self.subscribe_message_button_to_defect_display_count()
        self.columnconfigure(0, weight=1)  # to make the button able to fill the width
        self.rowconfigure(0, weight=1)  # to make the button able to fill the height

        # operator
        self.current_operator = tk.StringVar()

        # the buttons that aren't for a specific popup (add, settings, etc)
        self.controls_panel = IndependentControlsPanel(self, 'Control Panel', hide_option=self._hide_option,
                                                       grid_pad=self.pad, autohide_var=self._auto_hide,
                                                       autoshow_var=self._auto_show, ghost_hide=self._ghost_hide,
                                                       lam_num_controls=self.lam_num,
                                                       current_operator=self.current_operator,
                                                       )
        self.controls_panel.grid(row=2, column=0, sticky='we')
        self.hideables.append(self.controls_panel)

        # move the window to the front
        window_topmost(self)

        self._focus_out_func_id = self._set_focus_out_event()

        # if working on the code, print the tk structure
        if self.debugging:
            def recursive_print(tk_component, repeat=True):
                """Print the tkinter window/widget structure"""
                recurse_tk_structure(tk_component)
                if repeat:
                    self.after(5000, lambda x=None: recursive_print(self))

            self.after(1000, lambda: recursive_print(self))  # for debugging, prints out the tkinter structure
            recurse_hover(self.popup_frame)  # for debugging, shows widget info when mouse cursor moves over it

        # messages from flask
        self.new_messages = []
        self.flask_app = None
        self.after(1000, self.check_for_inbound_messages)

        # for querying the tag history database
        self._thist = TagHistoryConnector(f'lam{self.lam_num}')

        # when trying to close the window from the interface
        self.protocol("WM_DELETE_WINDOW", self.closing_handler)

        # try to position the window in the same place as last time
        self.reload_last_position()

        self.bind('<Configure>', self._save_this_position)
        self.bind('<Escape>', self.escape)

        self.after(5_000, self.ensure_on_top, True)

        self.mainloop()

    def reload_last_position(self):
        """Load the position information from last time the window was open."""

        try:
            self.last_pos_filepath = './untracked_config/last_position.txt'
            with open(self.last_pos_filepath, 'r') as pos_file:
                pos_dict = json.load(pos_file)
                lg.debug(f'last position loaded: {pos_dict}')
                self.geometry(f'''+{pos_dict['x']}+{pos_dict['y']}''')
        except FileNotFoundError as fnf:
            lg.error('File not found at %s', self.last_pos_filepath)  # if it doesn't exist then there is nothing to do
        except json.decoder.JSONDecodeError as jde:
            lg.error(exception_one_line(jde))
            blank_up(self.last_pos_filepath)

    def escape(self, event: tkinter.Event):
        """When the escape key is pressed, close the window."""

        lg.info('Escape key pressed, shutting down.')
        self.destroy()

    def _save_this_position(self, event: tkinter.Event):
        """Save the new window position for next time it opens."""

        if event.widget == self:
            pos_dict = {'x': event.x, 'y': event.y}
            try:
                with open(self.last_pos_filepath, 'r') as pos_file:
                    last_pos_dict = json.load(pos_file)
            except FileNotFoundError as fnf:
                exc_one_line = exception_one_line(fnf)
                lg.warning('Could not open previous position file, a new one will be created. %s', exc_one_line)
                last_pos_dict = None
            if last_pos_dict != pos_dict:
                with open(self.last_pos_filepath, 'w') as pos_file:
                    lg.debug(f'saving new position: {pos_dict}')
                    json.dump(pos_dict, pos_file, indent=4)

    def closing_handler(self):
        """When trying to close the window from the interface, hide instead."""

        self.hide_hideables()

    def _set_focus_out_event(self):
        """Set the auto hide window method for when focus is lost, returning the function id."""

        return self.bind("<FocusOut>", self._auto_hide_window)

    def _clear_focus_out_event(self):
        """Remove the auto hide window method when focus is lost binding."""

        self.unbind("<FocusOut>", self._focus_out_func_id)

    def _do_without_focus_out(self, callable_, *args, **kwargs):
        """Call the callable_ while auto hide is disabled.

        Some actions will cause the focus lost event to be raised even when "it shouldn't". This will
        disable the auto hide binding, call the function/method, then rebind the auto hide. Accepts args
        and kwargs for the callable.

        :param callable_: callable
        """

        self._clear_focus_out_event()
        self.update()
        callable_(*args, **kwargs)
        self._set_focus_out_event()

    def _auto_hide_window(self, event: tkinter.Event):
        """If auto-hide is selected, hide/shrink the window."""

        # check if auto hide is set, the window still hasn't focus, and it was the main window that lost focus
        if self._auto_hide.get() and self.focus_displayof() is None and event.widget is self:
            lg.debug('auto hiding window')
            self.hide_hideables(event)

    def _auto_show_window(self, event):
        """If auto-show is selected, show the window."""

        if self._auto_show.get():
            if self.popup_frame.current_defect_count():
                lg.debug('auto showing window')
                self.show_hideables(event)
            else:
                lg.debug('No defects to show. Staying hidden.')

    def subscribe_message_button_to_defect_display_count(self):
        """Subscribes the self.number_of_messages_button to the length of the defect list.
         The list calls a function to update the text on the button when the number of defects change."""

        def update_function(value):
            """Update the number_of_messages_button's text to the number of defects displayed."""
            self.number_of_messages_button.config(text=str(value))

        self.popup_frame.current_defects.subscribe(self.number_of_messages_button, update_function)

    def show_hideables(self, event=None):
        """Show the defect message panels, control panel, etc."""

        self.state(newstate='normal')  # in case minimized or maximized
        if not self.winfo_viewable() or self.message_button_geometry in self.geometry():
            self.attributes('-alpha', 1)  # opaque
            for hideable in self.hideables:
                hideable.grid()

            self.number_of_messages_button.grid_remove()  # hide the messages button
            self.full_sized()
            self.ensure_on_top()

    def full_sized(self):
        """Show the full sized window."""

        self.current_form = 'main_window'
        self.state(newstate='normal')
        self.maxsize(*self.full_window_geometry.split('x'))
        self.geometry(self.full_window_geometry)

    def button_sized(self):
        """Show the window button sized."""

        self.current_form = 'button'
        self.state(newstate='normal')
        self.maxsize(*self.message_button_geometry.split('x'))
        self.geometry(self.message_button_geometry)  # fixed size small window

    def hide_hideables(self, event=None):
        """Hide the components that are supposed to hide when the window 'shrinks'.

        :param event:
        """
        # this check is so that the window will not shrink when pressing buttons

        event_is_none = event is None  # so the hide_now button works
        window_not_focus = self.focus_displayof() is None  # so pressing buttons doesn't hide the window
        window_visible = self.winfo_viewable()  # so
        proceed = (event_is_none or window_not_focus) and window_visible
        lg.debug(f'{event=} {window_not_focus=} {proceed=} {self._auto_hide=}')

        if proceed:
            if self._hide_option.get() == 'v':
                lg.debug('withdrawing')
                self.withdraw()
            elif self._hide_option.get() == 'i':
                # self.attributes('-toolwindow', False)
                lg.debug('iconifying')
                self.iconify()
            elif self._hide_option.get() == 'b':
                # if not self.attributes('-toolwindow'):
                lg.debug('going to message button')
                # self.attributes('-toolwindow', True)  # hide max/minimize buttons
                for hider in self.hideables:
                    hider.grid_remove()
                self.number_of_messages_button.grid(row=0, column=0)

                self.button_sized()
            if self._ghost_hide.get():
                self.attributes('-alpha', self._ghost_fade.get() / 100.0)

    def check_for_inbound_messages(self):
        """Check the inbound queue for new defect messages and if there are any, send them to the MessagePanel."""

        while len(self.messages_from_flask):
            self.new_messages.append(self.messages_from_flask.pop())
        if self.new_messages:
            lg.debug('new messages: %s', self.new_messages)

            # if we haven't gotten the flask app via the queue yet, look for it
            for mindex, msg in enumerate(self.new_messages):
                if self.flask_app is None:
                    if msg.get('flask_app'):
                        self.flask_app = self.new_messages.pop(mindex)['flask_app']
                        lg.debug('Flask App received.')
                        self.after(2000, self.popup_frame.check_for_new_defects)
                elif msg.get('action'):
                    action_str = self.new_messages.pop(mindex)['action']
                    if action_str == 'shrink':
                        self.hide_hideables()
                    elif action_str == 'show':
                        self._auto_show_window(event=None)
                    elif action_str == 'show_force':
                        self.show_hideables()
                    elif action_str == 'check_defect_updates':
                        lg.debug('check for updates to defects')
                        self.popup_frame.check_for_new_defects()
                    elif action_str == 'reset_position':
                        self.geometry('+0+0')
                    elif action_str == 'restart_popup':
                        lg.info('Restarting Mahlo Defect Record Popup.')
                        restart_program()
        self.after(500, self.check_for_inbound_messages)

    def ensure_on_top(self, repeat=False):
        """Check if the window is visible,if not, bring it to the front."""

        lg.debug('on topping')
        self.deiconify()
        window_topmost(self)
        self.focus_get()

        if repeat:
            self.after(60_000, self.ensure_on_top, True)


class IndependentControlsPanel(tk.ttk.LabelFrame):
    """A frame with buttons that are not for specific defects, for the window itself."""

    def __init__(self, parent_container, text='This is the title', lam_num_controls=0, **kwargs):
        super().__init__(parent_container, text=text)
        self.parent = parent_container
        self._next_column = 0
        self.lam_num = lam_num_controls
        self.current_operator = kwargs.pop('current_operator')
        self.pad = kwargs.get('grid_pad')

        def add_new_defect():
            """Add a new defect to the database & popup window."""
            with self.parent.flask_app.app_context():  # TODO: add a get_flask method to parent and pass that in
                # create a new defect in the database, get the popup frame, tell it to update
                thist = self.winfo_toplevel()._thist
                lot_num = thist.current_lot_number()
                current_length = thist.current_mahlo_length()
                new_defect = DefectModel.new_defect(source_lot_number=lot_num, record_creation_source='operator',
                                                    mahlo_end_length=current_length, mahlo_start_length=current_length,
                                                    lam_num=self.lam_num)
                popup = self.parent.popup_frame  # TODO: replace this with a passed in method call
                popup.check_for_new_defects()

        # add a new defect button
        self.add_defect_button = tk.ttk.Button(self, text='New defect', command=add_new_defect)
        self.add_defect_button.grid(row=3, column=self.next_column(),
                                    padx=self.parent.pad['x'], pady=self.parent.pad['y'], sticky='ns')

        # hide button
        # getting an error claiming the parent doesn't have the method hide_hideables
        self.hide_button = tk.ttk.Button(self, text='Hide now', command=self.parent.hide_hideables)
        self.hide_button.grid(row=3, column=self.next_column(), sticky='ns', padx=self.parent.pad['x'],
                              pady=self.parent.pad['y'])

        # add what to do when hiding selection
        if kwargs.get('hide_option'):
            self._hide_selector = ttk.LabelFrame(self, text='Hide options')
            self._hide_selector.grid(row=3, column=self.next_column(), padx=self.pad['x'], pady=self.pad['y'],
                                     sticky='ns')

            # auto hide when losing focus
            self._autohide_toggle = ttk.Checkbutton(self._hide_selector, text='Autohide',
                                                    variable=kwargs['autohide_var'])
            self._autohide_toggle.grid(row=3, column=self.next_column(), sticky='ns', padx=self.pad['x'],
                                       pady=self.pad['y'])

            # unhide when gaining focus
            self._autoshow_toggle = ttk.Checkbutton(self._hide_selector, text='Autoshow',
                                                    variable=kwargs['autoshow_var'])
            self._autoshow_toggle.grid(row=3, column=self.next_column(), sticky='ns', padx=self.pad['x'],
                                       pady=self.pad['y'])

            # transparency
            self._ghost_fader = ttk.Checkbutton(self._hide_selector, text='Fade',
                                                variable=kwargs['ghost_hide'])
            self._ghost_fader.grid(row=3, column=self.next_column(), sticky='ns', padx=self.pad['x'],
                                   pady=self.pad['y'])

        # drop down to select the current operator
        active_operators_this_lam = OperatorModel.get_active_operators(self.lam_num)
        operator_names = [(op.first_name, op.last_name) for op in active_operators_this_lam]
        test_list = [' '.join((fn, ln)) for (fn, ln) in operator_names]
        self.operator_selector = ttk.OptionMenu(self, self.current_operator, *test_list, direction='above')
        self.operator_selector.grid(row=3, column=self.next_column(), sticky='ns', padx=self.pad['x'],
                                    pady=self.pad['y'])

        # restart the program button
        self.restart_button = ttk.Button(self, text='Restart', command=restart_program)
        self.columnconfigure(1000, weight=1)
        self.restart_button.grid(row=3, column=1000, sticky='e', padx=self.pad['x'],  # put it all the way to the right
                                 pady=self.pad['y'])

    def next_column(self):
        """Get an integer representing the next tk grid column to use."""

        self._next_column += 10
        return self._next_column
