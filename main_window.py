"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import tkinter as tk
from tkinter import ttk

from dev_common import add_show_messages_button, raise_above_all, recurse_hover, recurse_tk_structure, \
    style_component, \
    window_topmost
from fresk.models.defect import DefectModel
from log_setup import lg
# when called by RPC the directory may change and be unable to find the ttk theme file directory
from msg_window.popup_frame import DefectMessageFrame


class Popup(tk.Tk):
    """The main tkinter window that the defect_instance panels, controls, etc reside in."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.debugging = kwargs.get('debug')
        self.attributes('-toolwindow', True)

        # what to do when hiding
        self._hide_option = tk.StringVar()
        self._hide_option.set('b')  # default to button

        # communication with flask app
        inbound_queue = kwargs.get('inbound_queue')
        if inbound_queue is not None:
            self.messages_from_flask = inbound_queue
        else:
            lg.warning('No inbound_queue')

        outbound_queue = kwargs.get('outbound_queue')
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
        self.popup_frame = DefectMessageFrame(self, **grid_style_params)
        self.popup_frame.grid(row=1, column=0, sticky='nesw')
        self.hideables.append(self.popup_frame)

        # the button that shows while inactive, displays the number of new defects
        self.number_of_messages_button = add_show_messages_button(self, 0, self.show_hideables)
        self.number_of_messages_button.grid(row=0, column=0, sticky='nesw')
        self.subscribe_message_button_to_defect_display_count()
        self.columnconfigure(0, weight=1)  # to make the button able to fill the width
        self.rowconfigure(0, weight=1)  # to make the button able to fill the height

        # the buttons that aren't for a specific popup (add, settings, etc)
        self.controls_panel = IndependentControlsPanel(self, 'Control Panel', hide_option=self._hide_option,
                                                       grid_pad=self.pad)
        self.controls_panel.grid(row=2, column=0, sticky='we')
        self.hideables.append(self.controls_panel)

        # TODO: would making the window minimize (not just shrink) while the lam is running be good?
        #  it seems like it would

        # move the window to the front
        window_topmost(self)

        # self.bind("<FocusOut>", self.hide_hideables)
        # self.bind("<FocusIn>", show_hideables)

        lg.debug(self.hideables)

        # if working on the code, print the tk structure
        if self.debugging:
            def recursive_print(tk_component, repeat=True):
                """Print the tkinter window/widget structure"""
                recurse_tk_structure(self)
                if repeat:
                    self.after(15000, recursive_print)

            self.after(1000, recursive_print)  # for debugging, prints out the tkinter structure
            recurse_hover(self.popup_frame)  # for debugging, shows widget info when mouse cursor moves over it

        # messages from flask
        self.new_messages = []
        self.flask_app = None
        self.after(1000, self.check_for_inbound_messages)
        self.hide_hideables()
        self.mainloop()

    def subscribe_message_button_to_defect_display_count(self):
        """Subscribes the self.number_of_messages_button to the length of the defect list.
         The list calls a function to update the text on the button when the number of defects change."""

        def update_function(value):
            """Update the number_of_messages_button's text to the number of defects displayed."""
            self.number_of_messages_button.config(text=str(value))

        self.popup_frame.current_defects.subscribe(self.number_of_messages_button, update_function)

    def show_hideables(self, event=None):
        """Show the defect message panels, control panel, etc."""
        for hideable in self.hideables:
            hideable.grid()
        self.number_of_messages_button.grid_remove()
        self.geometry('')  # grow to whatever size is needed for all the messages and other widgets
        self.deiconify()
        self.state('normal')
        window_topmost(self)
        raise_above_all(self)

    def hide_hideables(self, event=None):
        """Hide the components that are supposed to hide when the window 'shrinks'.

        :param event:
        """
        # this check is so that the window will not shrink when pressing buttons
        if event is None or self.focus_get() is None:
            if self._hide_option.get() == 'v':
                lg.debug('withdrawing')
                self.withdraw()
            elif self._hide_option.get() == 'i':
                lg.debug('iconifying')
                self.iconify()
            elif self._hide_option.get() == 'b':
                lg.debug('going to message button')
                for hider in self.hideables:
                    hider.grid_remove()
                self.number_of_messages_button.grid(row=0, column=0)
                self.geometry('150x150')  # fixed size small window

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
                        self.after(2000, self.popup_frame.check_for_new_defects)
                elif msg.get('action'):
                    action_str = self.new_messages.pop(mindex)['action']
                    if action_str == 'shrink':
                        self.hide_hideables()
                    elif action_str == 'show':
                        self.show_hideables()
                    elif action_str == 'check_defect_updates':
                        lg.debug('check for updates to defects')
                        self.popup_frame.check_for_new_defects()
        self.after(500, self.check_for_inbound_messages)


class IndependentControlsPanel(tk.ttk.LabelFrame):
    """A frame with buttons that are not for specific defects, for the window itself."""

    def __init__(self, parent_container, text='This is the title', **kwargs):
        super().__init__(parent_container, text=text)
        self.parent = parent_container
        self._next_column = 0

        def add_new_defect():
            """Add a new defect to the database & popup window."""
            with self.parent.flask_app.app_context():  # TODO: add a get_flask method to parent and pass that in
                # create a new defect in the database, get the popup frame, make sure it has updated (to include the
                # new defect), get the panel for the new defect, call the panel's change attributes method
                new_defect = DefectModel.new_defect(record_creation_source='operator')
                popup = self.parent.popup_frame  # TODO: replace this with a passed in method call
                popup.check_for_new_defects()
                panel = popup.get_panel_by_defect_id(new_defect.id)
                panel.change_attributes()

        # add a new defect button
        self.add_defect_button = tk.ttk.Button(self, text='New defect', command=add_new_defect)
        self.add_defect_button.grid(row=3, column=self.next_column(),
                                    padx=self.parent.pad['x'], pady=self.parent.pad['y'])

        # hide button
        # getting an error claiming the parent doesn't have the method hide_hideables
        self.hide_button = tk.ttk.Button(self, text='Hide now', command=self.parent.hide_hideables)
        self.hide_button.grid(row=3, column=self.next_column())

        # add what to do when hiding selection
        if kwargs.get('hide_option'):
            self._hide_selector = ttk.LabelFrame(self, text='Hide options')
            self.pad = kwargs.get('grid_pad')
            self._hide_selector.grid(row=3, column=self.next_column(), padx=self.pad['x'], pady=self.pad['y'])
            options = ('Button', 'b'), ('Icon', 'i'), ('Vanish', 'v')
            for i, (option, optn) in enumerate(options):
                rb = ttk.Radiobutton(self._hide_selector, text=option, value=optn, variable=kwargs['hide_option'])
                rb.grid(row=3, column=i)

    def next_column(self):
        """Get an integer representing the next tk grid column to use."""

        self._next_column += 10
        return self._next_column

# TODO:
#  need to talk to some operators about how long until it makes sense to popup
#  doing it too soon they wouldn't have a chance and could be disruptive
#  respond (send it to a database?)
#  check that this will work over ssl (opening in the normal session) otherwise probably flask
