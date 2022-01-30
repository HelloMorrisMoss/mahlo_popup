"""Contains a tk.ttk.Entry that """

# from tkinter.ttk import *
import tkinter as tk
import tkinter.ttk
from tkinter import ttk

from dev_common import style_component
from log_setup import lg
from widgets.helpers import WhereWidget


class NumpadEntry(ttk.Entry):
	"""A tkinter.ttk.Entry that, when double_clicked, will show a number pad to edit the value."""

	def __init__(self, parent=None, **kw):
		super().__init__(parent, **kw)
		self.parent = parent
		self.bind('<Button-1>', self._quick_clicking)
		self._quick_clicks = 0

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

		lg.debug('Showing numpad')
		np = NumberPad(self)
		ww = WhereWidget(self)
		x, y = ww.belowcation()
		lg.debug(f'belowcation: {x=}, {y=} - {str(ww)}')
		np.position_here(x, y)
		self.selection_range(tk.END, tk.END)
	# np.withdraw()
	# np._root().update()
	# np.deiconify()


class NumberPad(tk.ttk.Frame):
	"""A number pad window that edits the passed Entry widget's value."""

	def __init__(self, entry: tkinter.ttk.Entry, prompt=None, **kwargs):
		super().__init__(entry.winfo_toplevel())
		self._button_dict = self.add_buttons()
		self._entry = entry
		self.bind("<FocusOut>", self.auto_close)

	# todo: make the frame resize to the entry?

	def add_buttons(self):
		button_labels = ['7', '8', '9',
		                 '4', '5', '6',
		                 '1', '2', '3',
		                 '.', '0', 'backspace',
		                 u'🡸', 'OK', u'🡺']
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
			self.close()
		elif label == u'🡸':
			# todo: if text is selected, unselect when using arrow keys
			self._entry.icursor(current_cursor_index - 1)
		elif label == u'🡺':
			self._entry.icursor(current_cursor_index + 1)
		else:
			# todo: if text is selected, replace selected text with label
			self._entry.insert(current_cursor_index, label)

	def auto_close(self, event):
		"""If the window lost focus and does not have it, close the window.
		
		This guards against closing when pressing the buttons.

		:param event: tkinter.Event
		"""
		if self.focus_displayof() is None and event.widget is self:
			self.close()

	def close(self):
		"""Close the NumPad window."""
		self.destroy()

	def position_here(self, x, y):
		"""Move the NumPad window to (x, y) on the screen."""
		# npw = WhereWidget(self)
		# self.geometry(f'{npw.w}x{npw.h}+{x}+{y}')
		# lg.debug(f'placing {x=}, {y=}')
		self.place(x=x, y=y)
		ww = WhereWidget(self)
	# lg.debug(str(ww))


if __name__ == '__main__':
	# the most basic of testing
	root = tk.Tk()
	root.geometry("800x800")
	style_component(root, r'..')
	txt_var = tk.StringVar()
	test_entry = NumpadEntry(root, textvariable=txt_var)
	# x_var = tk.IntVar()
	# y_var = tk.IntVar()
	# xentry = tk.Entry(variable=x_var)
	# yentry = tk.Entry(variable=y_var)
	# move_btn = tk.Button()
	test_entry.grid(row=0, column=0)


	def spot_for_breakpoint():
		root.after(1000, spot_for_breakpoint)


	root.after(1000, spot_for_breakpoint)

	root.mainloop()
