from pprint import pformat
from tkinter import ttk


class WhereWidget:
	"""Wrap the widget for conveniently accessing the location and size; also, the coordinates just below the
	widget."""

	def __init__(self, widget: ttk.Widget):
		self._widget = widget
		self.x = None
		self.y = None
		self.h = None
		self.w = None
		self.update()

	def update(self):
		self.x = self._widget.winfo_x()
		self.y = self._widget.winfo_y()
		self.h = self._widget.winfo_height()
		self.w = self._widget.winfo_width()

	def belowcation(self, pad_y=0):
		"""Get the location, (x, y) coordinates, on screen just below the widget.

		:param pad_y: additional vertical padding.
		:return: tuple
		"""

		_winx = self._widget.winfo_x()
		_winy = self._widget.winfo_y()
		return _winx, _winy + self.y + self.h + pad_y

	def __str__(self):
		return pformat(self.__dict__)
