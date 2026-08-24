"""
Adds touch-style scrolling functionality to widgets that support scan_mark/scan_dragto.

This module defines the `TouchScroller` class, which enables touch-style scrolling for widgets
like Canvas or Text. The functionality includes axis locking and drag thresholds, making it
suitable for handling intuitive touch gestures on nested widgets or containers.
"""


class TouchScroller:
    """
    Handles touch-based scrolling for widgets with optional drag thresholds and axis locking.

    This class provides functionality to enable touch scrolling for a given widget. It allows
    customization of drag thresholds, optional locking to a specific axis, and recursive application
    to all child widgets. The class is designed for integration with graphical user interfaces where
    smooth and intuitive touch scrolling behavior is needed.

    :ivar widget: The widget to which the touch scroller is attached.
    :type widget: Any
    :ivar drag_threshold: Minimum distance in pixels required to recognize a drag operation.
    :type drag_threshold: int
    :ivar lock_axis: Axis locking mode; can be 'x', 'y', or None.
    :type lock_axis: str or None
    :ivar tag: Unique identifier for the touch scroller instance to avoid conflicts with other
        bindings.
    :type tag: str
    """

    def __init__(self, scrollable_widget, drag_threshold=10, lock_axis=None):
        self.widget = scrollable_widget
        self.drag_threshold = drag_threshold
        self.lock_axis = lock_axis  # 'x', 'y', or None
        self.start_x = 0
        self.start_y = 0
        self.mark_x = 0
        self.mark_y = 0
        self.dragged = False

        # Unique tag for this scroller instance to avoid global interference
        self.tag = f"TouchScroll_{id(self)}"

        self.widget.bind_class(self.tag, "<Button-1>", self._on_press)
        self.widget.bind_class(self.tag, "<B1-Motion>", self._on_drag)
        self.widget.bind_class(self.tag, "<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.dragged = False

        # Translate pointer to widget coordinates
        self.mark_x = self.widget.winfo_pointerx() - self.widget.winfo_rootx()
        self.mark_y = self.widget.winfo_pointery() - self.widget.winfo_rooty()
        self.widget.scan_mark(self.mark_x, self.mark_y)
        return None  # Allow other bindings to trigger (like button press visual)

    def _on_drag(self, event):
        # Determine if we've moved enough to be considered a drag
        dx = abs(event.x_root - self.start_x)
        dy = abs(event.y_root - self.start_y)

        if dy > self.drag_threshold or dx > self.drag_threshold:
            self.dragged = True

        # Current pointer position
        curr_x = self.widget.winfo_pointerx() - self.widget.winfo_rootx()
        curr_y = self.widget.winfo_pointery() - self.widget.winfo_rooty()

        # Apply axis locking
        if self.lock_axis == 'y':
            curr_x = self.mark_x
        elif self.lock_axis == 'x':
            curr_y = self.mark_y

        # tk.Text and tk.Listbox do not support the 'gain' argument in the Python 
        # tkinter wrapper, defaulting to 10x speed. We use tk.call to force gain=1.
        try:
            self.widget.scan_dragto(curr_x, curr_y, gain=1)
        except TypeError:
            try:
                self.widget.tk.call(self.widget._w, 'scan', 'dragto', curr_x, curr_y, 1)
            except Exception:
                # Fallback to standard if direct call fails
                self.widget.scan_dragto(curr_x, curr_y)

        # Return "break" to prevent default widget behavior (like text selection)
        # while the user is attempting to scroll.
        return "break"

    def _on_release(self, event):
        if self.dragged:
            return "break"  # Suppress the click/release action if we dragged
        return None

    def apply_to(self, widget, exclude_types=None):
        """Recursively adds the touch scroll tag to a widget and all its children."""
        if exclude_types and any(isinstance(widget, t) for t in exclude_types):
            return

        tags = list(widget.bindtags())
        if self.tag not in tags:
            # Put it at the beginning to intercept release
            widget.bindtags((self.tag,) + tuple(tags))

        for child in widget.winfo_children():
            self.apply_to(child, exclude_types=exclude_types)
