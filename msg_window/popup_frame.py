from tkinter import ttk

from fresk.models.defect import DefectModel
from log_setup import lg
from msg_window.msg_panel import MessagePanel
from publishing_vars import PublishingLengthList


class DefectMessageFrame(ttk.Frame):
    """A popup window with messages to respond to. Create the window and messages based on a provided dictionary.

    """

    def __init__(self, parent_container, *args, **kwargs):
        """
        example_input_dict = {'messages': [{'title': 'Out of spec!',
                                        'msg_txt': {'template': template_str,
                                                    'timestamp': datetime.now().isoformat(),
                                                    'length_in_meters': oospec_len_meters},
                                        'buttons': ['removed!', 'oops!'],
                                        'msg_id': msg_id
                                        }
                                       for msg_id in ('msg123', 'msg456', 'msg789')],
                          'main_win': {'title': 'Messages received!'}
                          }
            messages: a list of defect_instance dictionaries. Each of which should include:
               title: a string title for the defect_instance frame
            main_win: a dictionary of parameters for the window apart from the messages.
                title: a string with the title for the main window.
        :param input_dict:
        """

        self.parent = parent_container
        super().__init__(self.parent)

        self.set_style(kwargs)

        self.dt_format_str = r'%I:%M %d-%b'  # the format for the datetime strftime to use for display

        self.grid(row=1, column=0, sticky='nesw', columnspan=3)

        # keep track of things
        self.messages_frames = []  # list of MessagePanel
        self.current_defects = PublishingLengthList()  # list of DefectModels
        self.message_panel_row = 0  # to keep the panels in order

        self.parent.after(5000, self.check_for_new_defects)  # give SQLalchemy time to connect to the database

    def get_panel_by_defect_id(self, id_num):
        """Get the panel for the defect with id_num.

        :param id_num: int
        :return: MessagePanel
        """
        for panel in self.messages_frames:
            if panel.defect_id == id_num:
                return panel
        return None

    def set_style(self, style_dict):
        """Incorporate the style dict parameters into the instance.

        :param style_dict: dict
        """
        styling = style_dict.get('style_settings')
        if styling:
            lg.debug('style provided')
            for k, v in styling.items():
                lg.debug(f'PopupFrame add {k}: {v}')
                setattr(self, k, v)

    def check_for_new_defects(self):
        """Check the database for new defects, if there are add new panels."""
        try:
            with self.parent.flask_app.app_context():
                new_defs = DefectModel.find_new()
        except AssertionError:
            lg.warning('Assertion error for sqlalchemy.')
            self.after(2000, self.check_for_new_defects)
            return

        lg.debug('new defects: %s', new_defs)
        for defect in new_defs:
            if defect not in self.current_defects:
                self.add_message_panel(defect)

        # if we have no defects, no need to be big
        if not self.current_defects:
            self.parent.hide_hideables()

    def get_message_rows(self):
        """Get a list of the rows that MessagePanels currently occupy.

        :return: list, [int, ...]
        """
        mrows = [msg_panel.msg_number for msg_panel in self.messages_frames]
        return mrows

    def add_message_panel(self, defect):
        """Add a message panel to the frame.

        :param defect: DefectModel
        :return: MessagePanel
        """
        if defect.id not in tuple(df.id for df in self.current_defects):
            self.message_panel_row += 1
            self.current_defects.append(defect)
            msg_frm = MessagePanel(self, defect, self.message_panel_row, dt_format_str=self.dt_format_str,
                                   pad={'x': self.pad['x'], 'y': self.pad['y']},
                                   _wgt_styles=self._wgt_styles)
            self.messages_frames.append(msg_frm)
            return msg_frm

    def show_number_of_msgs_button(self):
        """Show the button that has the count of defect messages."""
        self.number_of_messages_button.grid(row=0, column=0, sticky='nesw',
                                            rowspan=9, columnspan=3)
