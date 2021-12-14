import tkinter as tk
from pprint import pprint
from tkinter import ttk

from fresk.models.defect import DefectModel
from log_setup import lg
# from main_window import hover_enter_factory
from msg_panel import MessagePanel


class DefectMessageFrame(ttk.Frame):
    """A popup window with messages to respond to. Create the window and messages based on a provided dictionary.

    """

    def __init__(self, parent_container, input_dict=None, *args, **kwargs):
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

        # pprint(input_dict)
        # # set things up for the main window
        # self._defdic = input_dict

        # self.parent.title(self._defdic['main_win']['title'])  # TODO: this is a bad way to do this

        self.wgts = {}

        # variables for foam sections removed
        # self._removed_state_vars = {}
        # self.update_removed_vars(self._defdic['messages'])
        #
        # # for now set all the sections as removed
        # for msg_id, state_dict in self._removed_state_vars.items():
        #     state_dict['all'].set(True)

        # the format for the datetime strftime to use for display
        self.dt_format_str = r'%I:%M %d-%b'

        # the main frame
        self.main_frm = self
        self.main_frm.grid(row=1, column=0, sticky='nesw', columnspan=3)
        self.wgts['main_frame'] = self.main_frm

        self.messages_frames = []
        self.hideable = []

        # add the frames for the messages and the widgets therein
        # init_messages = self._defdic['messages']

        # add_show_messages_button(self, self.focus_gained_handler)

        self.current_defects = []
        self.message_panel_row = 0

        # self.add_message_panels(init_messages)
        self.parent.after(5000, self.update_message_panels)

    def set_style(self, kwargs):
        styling = kwargs.get('style_settings')
        if styling:
            lg.debug('style provided')
            for k, v in styling.items():
                lg.debug(f'PopupFrame add {k}: {v}')
                setattr(self, k, v)

    def update_message_panels(self, init_messages=None):
        """Check the database for new defects, if there are add new panels.

        :param init_messages: dict, deprecated
        """
        with self.parent.flask_app.app_context():
            new_defs = DefectModel.find_new()

        lg.debug('new defects: %s', new_defs)
        for defect in new_defs:
            if defect.id not in self.current_defects:
                lg.debug('New defect found')
                self.add_message_panel(defect)
            else:
                lg.debug('this defect already in current_defects')

        # if we have no defects, no need to be big
        if not self.current_defects:
            self.shrink()

    def get_message_rows(self):
        mrows = [msg_panel.msg_number for msg_panel in self.messages_frames]
        return mrows

    # def append_blank_message_panel(self, defect_id):
    #     mrows = self.get_message_rows()
    #     highest_row = max(mrows)
    #
    #     get_message_dict(defect_id, 1, 'At {timestamp}\nthere were {len_meters} meters oospec!')

    def add_message_panel(self, defect):
        self.message_panel_row += 1
        self.current_defects.append(defect.id)
        msg_frm = MessagePanel(self.main_frm, defect, self.message_panel_row, dt_format_str=self.dt_format_str,
                               pad={'x': self.pad['x'], 'y': self.pad['y']},
                               _wgt_styles=self._wgt_styles)
        self.messages_frames.append(msg_frm)

    # def refresh_data(self):
    #     """
    #     """
    #     # do nothing if the aysyncio thread is dead
    #     # and no more data in the queue
    #     if not self.thread.is_alive() and self.the_queue.empty():
    #         return
    #
    #     # refresh the GUI with new data from the queue
    #     while not self.the_queue.empty():
    #         key, data = self.the_queue.get()
    #         # self.data[key].set(data)
    #         # messages =
    #
    #     print('RefreshData...')
    #
    #     #  timer to refresh the gui with data from the asyncio thread
    #     self.after(1000, self.refresh_data)  # called only once!

    def update_removed_vars(self, messages):
        self._removed_state_vars.update({
            msg['msg_id']: {'all': tk.IntVar(), 'left': tk.IntVar(), 'left_center': tk.IntVar(), 'center': tk.IntVar(),
                            'right_center': tk.IntVar(), 'right': tk.IntVar()}
            for msg in messages})

    def focus_gained_handler(self, event):
        """When the window gains focus.

        :param event: tkinter.Event
        """
        lg.debug(event.widget == self.parent)
        if event.widget in (self,):
            lg.debug('Focus window!')
            self.grow()

    def grow(self):
        """Grow to show the foam removal messages."""
        # self.number_of_messages_button.grid_remove()
        for mf in self.messages_frames:
            mf.grid()
        self.main_frm.grid()
        self.parent.grid_propagate(True)
        self.parent.geometry('')

    def focus_lost_handler(self, event):
        """When the window loses focus (another window is clicked or otherwise switched to).

        :param event: tkinter.Event
        """

        if event.widget == self.parent:
            lg.debug('No longer focus window!')
            self.shrink()

    def shrink(self):
        """Shrink the window down to show only the 'show messages' button."""

        self.grid_remove()
        # for mf in self.messages_frames:
        #     mf.grid_remove()
        self.parent.update()
        self.parent.geometry('150x150')
        self.parent.grid_propagate(False)
        # self.show_number_of_msgs_button()

    def show_number_of_msgs_button(self):
        self.number_of_messages_button.grid(row=0, column=0, sticky='nesw',
                                            rowspan=9, columnspan=3)

    def wigify(self, obj):
        """Add a property 'wgts' that is an empty dictionary to the obj. (Intended for keeping track of tkinter widgets.)

        :param obj: any, the object to add the property.
        """
        setattr(obj, 'wgts', {})

    # def recurse_hover(self, wgts_dict, indent=0):
    #     """Recursively move down the nested tk objects by their 'custom' .wgt dict items adding a mouse-over function.
    #
    #     :param wgts_dict:
    #     :param indent:
    #     """
    #     for wname, wgt in wgts_dict.items():
    #         print('wd' + '\t' * indent, wgt, wgt.grid_info())
    #         hover_enter_factory(wgt)
    #         try:
    #             sub_wgts = getattr(wgt, 'wgts')
    #             if sub_wgts is not None:
    #                 self.recurse_hover(sub_wgts, indent=indent + 4)
    #         except AttributeError:
    #             pass
