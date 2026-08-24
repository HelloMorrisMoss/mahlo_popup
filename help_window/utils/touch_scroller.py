class TouchScroller:
    """
    Adds touch-style scrolling to a widget (Canvas or Text) that supports scan_mark/scan_dragto.
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

        self.widget.scan_dragto(curr_x, curr_y, gain=1)

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
