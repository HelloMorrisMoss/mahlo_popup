"""Contains a tk.ttk.Entry that """

# from tkinter.ttk import *
import tkinter as tk
import tkinter.ttk
from tkinter import ttk

from dev_common import style_component
from log_setup import lg


class NumpadEntry(ttk.Entry):
	"""A tkinter.ttk.Entry that, when double_clicked, will show a number pad to edit the value."""

	def __init__(self, parent, textvariable: tk.StringVar = None, *args, **kwargs):
		if textvariable is None:
			kwargs['textvariable'] = tk.StringVar()
		else:
			kwargs['textvariable'] = textvariable
		super().__init__(parent, *args, **kwargs)
		self.textvariable = kwargs['textvariable']
		self.parent = parent
		self.bind('<Button-1>', self._quick_clicking)
		self._quick_clicks = 0
		self._previous_value = self.get()  # the last value
		self.previous_values = [self._previous_value]  # all previous values (for undo)
		self._last_button_pressed = 'None'
		self.textvariable.trace_add('write', self._add_to_undo_list)
		self._undoing = False

	def _add_to_undo_list(self, *args):
		if not self._undoing:
			new_value = self.get()
			self.previous_values.append(new_value)
			self._previous_value = new_value

	def undo(self, *args):
		self._undoing = True
		while self.previous_values:
			undoed_value = self.previous_values.pop()
			if undoed_value != self._previous_value:
				self.textvariable.set(undoed_value)
				self._previous_value = undoed_value
				self.icursor(tk.END)
				break
		self._undoing = False

	def numpad_closed(self, event):
		"""If there are no entered numbers, but there had been before, clear the numbers."""
		self.winfo_toplevel().focus_force()
		if self.get() == '' and self._previous_value != '':
			self.insert(0, self._previous_value)

	def _quick_clicking(self, event=None):
		"""Count the recent repeated and rapid clicks on the _entry, if it was double_clicked open the number pad.

		:param event: tkinter.Event
		"""
		if self._quick_clicks == 1:
			self._reset_quick_clicks()
			self.show_numpad()
		else:
			self._quick_clicks += 1

			def unchanged_quick_clicks():
				print('reset quick')
				if self._quick_clicks == getattr(self, '_quick_clicks'):
					self._reset_quick_clicks()

			self.after(500, unchanged_quick_clicks)

	def _reset_quick_clicks(self):
		"""Set the count of quick clicks to 0."""
		self._quick_clicks = 0

	def show_numpad(self):
		"""Show a new window with a number pad to edit the _entry's value."""

		# save and clear the current value
		self._previous_value = self.get()
		# self.delete(0, tk.END)

		np = NumberPad(self)
		np.place(in_=self, relx=0, rely=1)
		self.after(10, lambda: self.selection_clear())


class NumberPad(tk.ttk.Frame):
	"""A number pad window that edits the passed Entry widget's value."""

	def __init__(self, entry: NumpadEntry, prompt=None, **kwargs):
		super().__init__(entry.winfo_toplevel())
		self._button_dict = self.add_buttons()
		self._entry = entry
		self._original_value = self._entry.get()

		# this works but limits the reusability
		self.winfo_toplevel().bind_all("<Button-1>", self.auto_close)  # close the number pad when losing focus

	# todo: make the frame resize to the entry? place(...relwidth=1) just truncated the buttons
	def add_buttons(self):
		button_labels = ['7', '8', '9',
		                 '4', '5', '6',
		                 '1', '2', '3',
		                 '.', '0', 'backspace',
		                 u'🡸', 'OK', u'🡺',
		                 'undo', 'revert', 'clear'
		                                   'today']
		# TODO: clear, undo, and cancel buttons here?

		buttons_dict = {}
		padx = 1
		pady = padx

		num_cols = 3
		for row, column, label in [((i // num_cols), (i % num_cols), item) for i, item in enumerate(button_labels)]:
			command = lambda event, lambel=label: self.click(lambel)
			btn = ttk.Button(self, text=label, takefocus=False)
			btn.bind('<Button-1>', command)
			btn.grid(row=row, column=column, padx=padx, pady=pady)
			buttons_dict[label] = btn

		return buttons_dict

	def click(self, label):
		"""Edit the _entry value.

		:param label: 
		"""
		current_cursor_index = self._entry.index(tk.INSERT)
		if label == 'backspace':
			# todo: if text is selected, delete it
			self._entry.delete(current_cursor_index - 1, current_cursor_index)
		elif label == 'OK':
			self.close_numpad()
		elif label == u'🡸':
			# todo: if text is selected, unselect when using arrow keys
			self._entry.icursor(current_cursor_index - 1)
		elif label == u'🡺':
			self._entry.icursor(current_cursor_index + 1)
		elif label == 'clear':
			self.clear()
		elif label == 'revert':
			self.replace_all(self._original_value)
			self._entry.icursor(tk.END)
		elif label == 'undo':
			self._entry.undo()
		elif label == 'today':
			import datetime
			datetime.datetime.today()
			self.replace_all(datetime.datetime.today().isoformat()[:10].replace('-', ''))
		else:
			# todo: if text is selected, replace selected text with label
			self._entry.insert(current_cursor_index, label)

	def replace_all(self, new_value):
		self.clear()
		self._entry.insert(0, new_value)

	def clear(self):
		self._entry.delete(0, tk.END)

	def auto_close(self, event):
		"""If the window lost focus and does not have it, close the window.
		
		This guards against closing when pressing the buttons.

		:param event: tkinter.Event
		"""

		# if it's not the numpad or descendants
		if not str(event.widget).startswith(str(self)):
			self.close_numpad()

	def close_numpad(self):
		"""Close the NumPad window."""

		# if nothing has been entered, but there was a value before, revert
		if self._entry.get() == '' and self._original_value != '':
			self.replace_all(self._original_value)
		self.winfo_toplevel().focus_force()
		self._entry.focus_force()
		self.winfo_toplevel().unbind_all("<Button-1>")
		self.destroy()


class UpDownButtonFrame(tk.ttk.LabelFrame):
	"""A frame with up and down buttons that increments a value displayed on a label."""

	def __init__(self, parent, ud_defect, variable, *args, **kwargs):
		# keywords not intended for the LabelFrame
		incr_vals = kwargs.pop('increment_values', None)
		if not incr_vals:
			lg.debug('using default incr_vals')
			incr_vals = [1]
		self._field_name = kwargs.pop('field_name')

		super().__init__(parent, *args, **kwargs)
		self.defect = ud_defect
		self.length_var = variable
		self.length_var.set(str(ud_defect.length_of_defect_meters))
		self.length_var.trace('w', self.update_length)

		# todo: this could be its own class
		self.up_frame = tk.ttk.Frame(self)
		self.up_frame.grid(row=10, column=10, sticky='ew')
		# self.up_frame.grid_propagate(0)  # turns off auto sizing based on children, but currently shrinks to nothing
		self.down_frame = tk.ttk.Frame(self)
		self.down_frame.grid(row=70, column=10, sticky='ew')

		# add the increment buttons
		last_column = 10
		pad_val = 1

		for inc_val in incr_vals:
			# what's up button? the button that makes the length go up, and down down
			up_button = LengthButton(self.up_frame, self.length_var, 'up',
			                         text=f'{inc_val}', increment_magnitude=inc_val)

			up_button.grid(row=20, column=last_column, sticky='nsew', padx=pad_val, pady=pad_val)

			down_button = LengthButton(self.down_frame, self.length_var, 'down',
			                           text=f'{inc_val}', increment_magnitude=inc_val)
			down_button.grid(row=70, column=last_column, sticky='nsew', padx=pad_val, pady=pad_val)

			last_column += 10

		# the '+' label
		col_span = last_column
		self.up_label = tk.ttk.Label(self.up_frame, text='+')
		self.up_label.config(font=(None, 14))
		self.up_label.grid(row=10, column=10, columnspan=col_span)

		self._top_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
		self._top_divider.grid(row=5, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

		self._top_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
		self._top_divider.grid(row=30, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

		# label displaying the value
		self.length_entry = NumpadEntry(parent=self, textvariable=self.length_var, width=11, justify='center')
		self.length_entry.config(font=(None, 20))
		self.length_entry.grid(row=40, column=10, rowspan=2, columnspan=col_span, padx=(2, 2))

		self._bottom_divider = tk.ttk.Separator(self, orient=tk.HORIZONTAL)
		self._bottom_divider.grid(row=50, column=10, columnspan=col_span, sticky='ew', padx=2, pady=2)

		# the '-' label
		self.down_label = tk.ttk.Label(self.down_frame, text='-')
		self.down_label.config(font=(None, 14))
		self.down_label.grid(row=80, column=10, columnspan=col_span)

	def update_length(self, *args):
		"""Update the label and ud_defect value. TODO: pull the ud_defect parts out of here, make this publish -->
		reusable.

		:param args: tuple, unused tkinter arguments.
		"""
		new_val = self.length_var.get()
		setattr(self.defect, self._field_name, float(new_val))


class LengthButton(tk.ttk.Button):
	def __init__(self, parent, length_var, direction_str, *args, **kwargs):

		icr_mag = kwargs.pop('increment_magnitude', None)
		self.increment_magnitude = icr_mag if icr_mag else 1

		super().__init__(parent, *args, **kwargs)
		self.config(width=3)
		self.length_var = length_var
		self.parent = parent

		if direction_str == 'up':
			self.increment_val = self.increment_magnitude
		elif direction_str == 'down':
			self.increment_val = -1 * self.increment_magnitude

		self.bind('<Button-1>', self.increment)

	def increment(self, *args):
		"""Increase or decrease the variable.

		:param args: tuple, unused tkinter params.
		"""

		self.length_var.set(str(round(float(self.length_var.get()) + self.increment_val, 2)))


if __name__ == '__main__':
	# the most basic of testing
	root = tk.Tk()
	root.geometry('400x400+2500+200')  # place it on the second monitor for testing
	style_component(root, r'..')
	txt_var = tk.StringVar()
	test_entry = NumpadEntry(root, textvariable=txt_var)
	test_entry.grid(row=0, column=0)

	txt_var2 = tk.StringVar()
	test_entry2 = NumpadEntry(root, textvariable=txt_var2)
	test_entry2.grid(row=0, column=1)
	# root.bind_all("<1>", lambda event: event.widget.focus_set())
	root.mainloop()
