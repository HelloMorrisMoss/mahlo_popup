from tkinter import ttk


class WhereWidget:
	"""Wrap the widget for conveniently accessing the location and size; also, the coordinates just below the
	widget."""

	def __init__(self, widget: ttk.Widget):
		self._widget = widget
		self.x = self._widget.winfo_x()
		self.y = self._widget.winfo_y()
		self.h = self._widget.winfo_height()
		self.w = self._widget.winfo_width()

	def belowcation(self, pad_y=0):
		"""Get the location, (x, y) coordinates, on screen just below the widget.

		:param pad_y: additional vertical padding.
		:return: tuple
		"""

		_winx = self._widget.winfo_rootx()
		_winy = self._widget.winfo_rooty()
		return _winx, _winy + self.y + self.h + pad_y
