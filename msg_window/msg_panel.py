"""Contains the panel that displays the defect information and interface."""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

import sqlalchemy.exc

from dev_common import StrCol
from fresk.models.lam_operator import OperatorModel
from log_setup import lg
from msg_window.defect_attributes import DefectTypePanel, HorizontalNumButtonSelector, LengthSetFrames, LotNumberEntry
from widgets.roll_removed_toggles import RollRemovedToggles


class MessagePanel(tk.ttk.LabelFrame):
    def __init__(self, parent, current_defects, defect_instance=None, row=0, **kwargs):
        super().__init__(parent)
        self.config(text=f'Defect #{defect_instance.id}')
        self.msg_number = row

        self.current_defects = current_defects

        if not kwargs.get('pad'):
            kwargs['pad'] = {'x': 2, 'y': 2}
        if not kwargs.get('dt_format_str'):
            self.dt_format_str = r'%I:%M %d-%b'
        self.grid_params_ = dict(column=0, row=row, padx=kwargs['pad']['x'], pady=kwargs['pad']['y'], sticky="nesw")
        self.grid(**self.grid_params_)
        self.parent = parent

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.hideables = []
        self.defect_interface = defect_instance
        self.defect_id = self.defect_interface.id
        self.message_text_template = 'lot  # {lot_number}\n' \
                                     '{timestamp} on lam{lam_num}\n' \
                                     '{len_meters} meters oospec\n' \
                                     'starting at Mahlo {mahlo_start_length}\n' \
                                     'ending at Mahlo {mahlo_end_length}\n' \
                                     'due to {dtype}\n' \
                                     'defect id: {defect_id}'

        sides_to_defect_columns_dict = {'left': 'rem_l', 'left_center': 'rem_lc',
                                        'center': 'rem_c', 'right_center': 'rem_rc', 'right': 'rem_r'}

        self._removed_vals = {k: StrCol(self.defect_interface, col) for k, col in sides_to_defect_columns_dict.items()}
        self._removed_vals.update({'all': tk.StringVar()})

        # add the tabbed frames
        self._tabframe = ttk.Notebook(self)
        self._tabframe.grid(row=0, column=0, sticky='nesw')

        self._lot_rolls_type_frame = ttk.Frame(self)
        self._lengths_frame = ttk.Frame(self)
        self._confirm_frame = ttk.Frame(self)

        self._tabframe.add(self._lot_rolls_type_frame, text='lot #, rolls, defect type')
        self._tabframe.add(self._lengths_frame, text='lengths')
        self._tabframe.add(self._confirm_frame, text='confirmation')

        # update the label text when changing tabs
        self._tabframe.bind('<<NotebookTabChanged>>', self.update_message_text)

        # if it's an auto-detected defect, they hopefully only need to confirm it, start there
        if self.defect_interface.record_creation_source != 'operator':
            self._tabframe.select(self._tabframe.index('end') - 1)

        # lot #, rolls, defect type panel
        self.lot_number_selector = LotNumberEntry(self._lot_rolls_type_frame, self.defect_interface)
        self.lot_number_selector.grid(row=0, column=0, padx=2, pady=2, sticky='ns')

        self.defect_type_panel = DefectTypePanel(self._lot_rolls_type_frame, self.defect_interface)
        self.defect_type_panel.grid(row=0, column=1, sticky='ns', padx=2)

        self.number_of_finished_rolls = tk.IntVar()
        self._roll_count_selector = HorizontalNumButtonSelector(self._confirm_frame, self.defect_interface,
                                                                variable=self.number_of_finished_rolls)
        self._roll_count_selector.grid(row=1, column=1)

        self._lot_rolls_type_frame.rowconfigure(0, weight=1)  # make the next button fill the full length
        self.advance_to_lengths_button = ttk.Button(self._lot_rolls_type_frame, text='next',
                                                    command=lambda: self._tabframe.select(1))
        self.advance_to_lengths_button.grid(row=0, column=10, rowspan=10, sticky='ns')

        # length panel
        self.length_panel = LengthSetFrames(self._lengths_frame, self.defect_interface)
        self.length_panel.grid(row=0, column=0, sticky='nesw')

        self.advance_to_confirm_button = ttk.Button(self._lengths_frame, text='next',
                                                    command=lambda: self._tabframe.select(2))
        self.advance_to_confirm_button.grid(row=0, column=10, rowspan=10, sticky='nse')
        self._lengths_frame.columnconfigure(10, weight=1)  # so this next button can stick to the right and match

        # confirmation frame
        self.message_label = self._add_message_display_label(self._confirm_frame)
        self.update_message_text()
        self.hideables.append(self.message_label)

        self._add_buttons(self._confirm_frame)

    def _add_message_display_label(self, parent):
        """A ttk label displaying information about the defect. Clicking the label will allow changes to be made.

        :param parent: tkinter container, the parent container to add the label to.
        :return: tk.ttk.Label
        """

        label = tk.ttk.Label(parent)
        grid_params = dict(column=0, row=0, padx=self.pad['x'], pady=self.pad['y'], sticky="w")
        setattr(label, 'grid_params_', grid_params)
        label.grid(**grid_params)

        return label

    # add a popup to change the defect attributes when clicking the label
    def change_attributes(self, event=None):
        lg.debug('changing defect type')
        self.defect_type_panel.grid()
        self.hide_hideables()

    def refresh_panel(self):
        self.update_message_text()
        # self._change_toggle_count()

    def hide_hideables(self):
        """Hide (.remove_grid) on all widgets that have been added to the hideables list."""
        lg.debug('hideable: %s', self.hideables)
        for hideable in self.hideables:
            hideable.grid_remove()

    def show_hideables(self, event=None):
        """Hide (.remove_grid) on all widgets that have been added to the hideables list."""
        for hideable in self.hideables:
            lg.debug(hideable)
            hideable.grid(**hideable.grid_params_)

    def update_message_text(self, *args):
        """Update the message label with any changes."""

        msg_text = self.message_text_template.format(
            lot_number=self.defect_interface.source_lot_number,
            timestamp=self.defect_interface.defect_end_ts.strftime(self.dt_format_str),
            len_meters=self.defect_interface.length_of_defect_meters,
            dtype=self.defect_interface.defect_type,
            defect_id=self.defect_interface.id,
            mahlo_start_length=self.defect_interface.mahlo_start_length,
            mahlo_end_length=self.defect_interface.mahlo_end_length,
            lam_num=self.defect_interface.lam_num,
            )
        self.message_label.config(text=msg_text)

    def _add_buttons(self, parent):
        """Add the button frames and their widgets to the parent frame.

        :param message: dict, the defect_instance dictionary
        :param parent: tkinter.Frame, or LabelFrame or similar.
        """

        # TODO: it may be worthwhile at some point to extract the toggle panel to its own class
        # add the removed foam toggles
        self._removed_toggles = RollRemovedToggles(parent, self.defect_interface)
        self.number_of_finished_rolls.trace_add('write', self._removed_toggles.update_number_of_toggles)
        self._removed_toggles.grid(row=0, column=1)

        # add the save button
        send_btn = tk.ttk.Button(parent, style='Accent.TButton', text='Save', command=self.save_response)
        send_grid_params = {'column': 12, 'row': 0,
                            'rowspan': 10,
                            'sticky': 'nesw'}

        parent.columnconfigure(12, weight=1)
        parent.rowconfigure(0, weight=1)
        send_btn.grid(**send_grid_params)
        send_btn.grid(sticky='nse')
        setattr(send_btn, 'msg_id', self.defect_interface.id)
        setattr(send_btn, 'side', 'send')

    def save_response(self, event=None):
        """Save the changes made to the database.

        :param event: tkinter.Event, (optional)
        """

        lg.debug('Saving defect record: %s', self.defect_interface)
        now_ts = datetime.now()  # todo: make this part of .save_to_database and use the database time
        self.defect_interface.entry_modified_ts = now_ts
        self.defect_interface.operator_saved_time = now_ts

        # get the operator name
        top_level_win = self.winfo_toplevel()
        op_name = top_level_win.current_operator.get().split(' ')
        filter_val_first = OperatorModel.first_name == op_name[0]
        filter_val_last = OperatorModel.last_name == op_name[1]
        try:
            operator_db = OperatorModel.query.filter(filter_val_first).filter(filter_val_last).all()[0]
        except sqlalchemy.exc.PendingRollbackError:
            OperatorModel.scoped_session.rollback()
            lg.error('Rollback error trying to fetch operator data.')
            return
        except IndexError:
            lg.debug('IndexError fetching operator from database. Check selected operator.')
            top_level_win.event_generate('<<OperatorNotFound>>')
            return
        self.defect_interface.operator_initials = operator_db.initials
        self.defect_interface.operator_list_id = operator_db.id
        self.defect_interface.save_to_database()
        self.current_defects.pop(self.current_defects.index(self.defect_interface))
        self.destroy()


# if __name__ == '__main__':
#     from fresk.models.defect import DefectModel
#     from fresk.flask_app import start_flask_app
#     from threading import Thread
#     from collections import deque
#     import time
#
#     root = tk.Tk()
#     in_out_q = deque()
#     flask_thread = Thread(target=start_flask_app, args=(in_out_q, in_out_q))
#     flask_thread.start()
#     while not len(in_out_q):
#         lg.debug(f'waiting for flask {in_out_q}')
#         time.sleep(1)
#     app = in_out_q.pop()['flask_app']
#     with app.app_context():
#         dd = DefectModel.new_defect()
#     MessagePanel(root, dd, 0)
if __name__ == '__main__':
    from dev_common import style_component


    class DummyDefect(object):
        """For testing the attributes window."""

        def __init__(self):
            self.id = 99
            self.defect_type = 'puckering'
            self.rolls_of_product_post_slit = 3
            self.length_of_defect_meters = 1.0
            self.record_creation_source = 'operator'


    root = tk.Tk()
    style_component(root, '..')
    defect1 = DummyDefect()
    lg.debug(defect1.__dict__)

    for frame in ((DefectTypePanel, 'type'), (LengthSetFrames, 'length'), (HorizontalNumButtonSelector, 'number')):
        frm = frame[0](root, defect1)
        frm.grid()

    root.mainloop()
    print(defect1.__dict__)
