"""Contains a tk.ttk.Entry that """

# from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk

from dev_common import style_component
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

		np = NumberPad(self)
		np.withdraw()
		np._root().update()
		x, y = WhereWidget(self).belowcation()
		np.position_here(x, y)
		np.deiconify()


# class NumberPad(simpledialog.Dialog):
class NumberPad(tk.Toplevel):
	"""A number pad window that edits the passed Entry widget's value."""

	def __init__(self, entry, prompt=None, **kwargs):
		super().__init__(entry)
		self._button_dict = self.add_buttons()
		self._entry = entry
		self.bind("<FocusOut>", self.auto_close)

	def add_buttons(self):
		button_labels = ['7', '8', '9',
		                 '4', '5', '6',
		                 '1', '2', '3',
		                 '.', '0', '<']

		buttons_dict = {}

		num_cols = 3
		for row, column, label in [((i // num_cols), (i % num_cols), item) for i, item in enumerate(button_labels)]:
			command = lambda lambel=label: self.click(lambel)
			btn = ttk.Button(self, text=label, command=command, takefocus=False)
			btn.grid(row=row, column=column)
			buttons_dict[label] = btn

		# add the OK button
		command = lambda lambel='OK': self.click(lambel)
		ok_button = ttk.Button(self, text='OK', command=command)
		ok_button.grid(row=row + 1, column=0, columnspan=100)

		return buttons_dict

	def click(self, label):
		"""Edit the _entry value.

		:param label: 
		"""
		if label == '<':
			print('delete')
			currentText = self._entry.get()
			self._entry.delete(0, tk.END)
			self._entry.insert(0, currentText[:-1])
		elif label == 'OK':
			self.close()
		else:
			currentText = self._entry.get()
			self._entry.delete(0, tk.END)
			self._entry.insert(0, currentText + label)

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
		npw = WhereWidget(self)
		self.geometry(f'{npw.w}x{npw.h}+{x}+{y}')


if __name__ == '__main__':
	# the most basic of testing
	root = tk.Tk()
	root.geometry("200x200")
	style_component(root, r'..')
	txt_var = tk.StringVar()
	test_entry = NumpadEntry(root, textvariable=txt_var)
	test_entry.grid(row=0, column=0)
	root.mainloop()
