"""To add a popup window to the Mahlo HMI PC at the laminators. Designed to be called from the command line over ssl."""

import argparse
import datetime
import json
import tkinter as tk
import os
from pprint import pprint

from fresk.models.defect import DefectModel
from fresk.sqla_instance import fsa

from log_setup import lg

from dev_common import recurse_hover, recurse_tk_structure, add_show_messages_button

# when called by RPC the directory may change and be unable to find the ttk theme file directory
from popup_frame import DefectMessageFrame
from publishing_vars import publishing_var

os.chdir(r'C:\Users\lmcglaughlin\PycharmProjects\mahlo_popup')


# TODO: why not just have the popup ask (get request) flask if it has any current messages every second?
#  because then the defect would need to be changed from a DefectModel or DefectResourse to a json string and back to
#  useful values and then sent back again the same way

class Popup(tk.Tk):
    """The main tkinter window that the defect_instance panels, controls, etc reside in."""

    def __init__(self, input_dict=None, *args, **kwargs):
        super().__init__()
        self.debugging = kwargs.get('debug')
        self.attributes('-toolwindow', True)

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

        # # todo: publishing var (possibly nested) to go from the length(self.current_defects) -> the show button label

        # styling
        self.tk.call("source", "Azure-ttk-theme-main/Azure-ttk-theme-main/azure.tcl")
        self.tk.call("set_theme", "dark")
        # frame padding
        self.pad = dict(x=5, y=3)
        self._wgt_styles = {'toggle': 'Switch.TCheckbutton', 'labelframe': 'Card.TFrame'}

        params = {'style_settings': {'pad': self.pad, '_wgt_styles': self._wgt_styles}}

        # list of components that need to 'hide' when not the lam is running
        self.hideables = []

        # self.
        self.number_of_messages_button = add_show_messages_button(self, 0, self.show_hideables)
        self.number_of_messages_button.grid(row=0, column=0, sticky='nesw')

        self.columnconfigure(0, weight=1)  # to make the button able to fill the width
        self.rowconfigure(0, weight=1)  # to make the button able to fill the height

        # where the messages about defect appear with their toggles/save buttons
        self.popup_frame = DefectMessageFrame(self, input_dict, **params)
        self.popup_frame.grid(row=1, column=0, sticky='nesw')
        self.hideables.append(self.popup_frame)

        # the buttons that aren't for a specific popup (add, settings, etc)
        self.controls_panel = IndependentControlsPanel(self, 'Control Panel')
        self.controls_panel.grid(row=2, column=0, sticky='we')
        self.hideables.append(self.controls_panel)

        if input_dict is None:
            lg.debug('no messages, hiding hideables')
            # lg.debug(input_dict['messages'])
            self.hide_hideables()
        else:
            lg.debug('messages, showing hideables')
            self.show_hideables()

        # TODO: would making the window minimize while the lam is running be good? it seems like it would
        # move the window to the front
        self.lift()
        self.attributes('-topmost', True)
        # self.root.after_idle(self.root.attributes, '-topmost', False)

        self.bind("<FocusOut>", self.hide_hideables)
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

        self.mainloop()

    def show_hideables(self, event=None):
        """Show the defect message panels, control panel, etc."""
        for hideable in self.hideables:
            hideable.grid()
        self.number_of_messages_button.grid_remove()
        self.geometry('')  # grow to whatever size is needed for all the messages and other widgets

    def hide_hideables(self, event=None):
        """Hide the components that are supposed to hide when the window 'shrinks'.

        :param event:
        """
        # this check is so that the window will not shrink when pressing buttons
        if event is None or self.focus_get() is None:
            for hideable in self.hideables:
                hideable.grid_remove()
            self.number_of_messages_button.grid(row=0, column=0)
            self.geometry('150x150')  # fixed size small window

    def check_for_inbound_messages(self):
        """Check the inbound queue for new defect messages and if there are any, send them to the MessagePanel."""

        while len(self.messages_from_flask):
            self.new_messages.append(self.messages_from_flask.pop())
        if self.new_messages:
            # if True:
            lg.debug('new messages: %s', self.new_messages)

            # if we haven't gotten the flask app via the queue yet, look for it
            if self.flask_app is None:
                for mindex, msg in enumerate(self.new_messages):
                    if msg.get('flask_app'):
                        self.flask_app = self.new_messages.pop(mindex)['flask_app']
                        self.popup_frame.update_message_panels()
            else:
                # if we do have a flask app, use it for the messages
                # with self.flask_app:
                # # TODO: this needs to pop the message
                # defmodel = self.new_messages[0]['defect_model']
                # session = self.new_messages[0]['session']
                # app_context = self.new_messages[0]['flask_context']
                # # pprint(defmodel.json())
                # defmodel.bursting = False
                # from pprint import pprint
                # pprint(dir())
                #
                # # with app_context:
                # #     defmodel.save_to_database()
                # # with self.flask_app:
                # #     defmodel.save_to_database()
                # TODO: now it seems so obvious... once you have access to the flask app, just import the
                #  model and create the context here
                #  ps: this is still a context passed through, change it for the app so each time it can
                #  be a new session - or can the app just be imported?
                with self.flask_app.app_context():
                    # this is just for testing, it flips the bursting column boolean
                    # defm = DefectModel.find_by_id(8)
                    # defm.bursting = not defm.bursting
                    # defm.save_to_database()

                    # this is effectively getting all the rows as defect models
                    # pprint(DefectModel.find_all())

                    # # this is getting all the defects that have not been modified
                    new_defects = DefectModel.find_new()
                    # pprint(new_defects)
                    # # this is changing one of their modified times so the results change
            #         # new_defects[0].entry_modified_ts = datetime.datetime.now()
            #         # new_defects[0].save_to_database()
            # # self.popup_frame.update_message_panels()
        self.after(5000, self.check_for_inbound_messages)
        # self.popup_frame.add_message_panels(new_messages)


class IndependentControlsPanel(tk.ttk.LabelFrame):
    def __init__(self, parent_container, text='This is the title'):
        super().__init__(parent_container, text=text)
        self.parent = parent_container

        # self.dummy_label = tk.ttk.Label(self, text='words on a label')
        # self.dummy_label.grid(row=3, column=0)

        def add_new_defect():
            """Add a new defect to the database & popup window."""
            with self.parent.flask_app.app_context():
                new_defect = DefectModel.new_defect(record_creation_source='operator')
                lg.debug(new_defect)
                popup = self.parent.popup_frame
                popup.update_message_panels()

        # TODO: this may be adding multiple defects?
        # add a new defect button
        self.add_defect_button = tk.ttk.Button(self, text='Add removed', command=add_new_defect)
        self.add_defect_button.grid(row=3, column=10)

        # # hide button
        # # getting an error claiming the parent doesn't have the method hide_hideables
        # self.hide_button = tk.ttk.Button(self, text='Hide now', command=self.parent.hide_hideables)
        # self.add_defect_button.grid(row=3, column=20)


# TODO:
#  need to talk to some operators about how long until it makes sense to popup
#  doing it too soon they wouldn't have a chance and could be disruptive
#  respond (send it to a database?)
#  check that this will work over ssl (opening in the normal session) otherwise probably flask
