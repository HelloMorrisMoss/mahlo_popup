"""
Adds touch-style scrolling functionality to widgets that support scan_mark/scan_dragto.

This module defines the `TouchScroller` class, which enables touch-style scrolling for widgets
like Canvas or Text. The functionality includes axis locking and drag thresholds, making it
suitable for handling intuitive touch gestures on nested widgets or containers.
"""

import time
import tkinter as tk

class TouchScroller:
    """
    Handles touch-based scrolling for widgets with optional drag thresholds, axis locking,
    and kinetic inertia.

    This class provides functionality to enable touch scrolling for a given widget. It allows
    customization of drag thresholds, optional locking to a specific axis, recursive application
    to all child widgets, and natural-feeling kinetic scrolling with interruption support.

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

    def __init__(self, scrollable_widget, drag_threshold=10, lock_axis=None, friction=0.9, min_velocity=1.0):
        self.widget = scrollable_widget
        self.drag_threshold = drag_threshold
        self.lock_axis = lock_axis  # 'x', 'y', or None
        self.friction = friction  # Exponential decay factor (0 to 1)
        self.min_velocity = min_velocity  # Threshold to stop kinetic scrolling
        
        self.start_x = 0
        self.start_y = 0
        self.mark_x = 0
        self.mark_y = 0
        self.dragged = False

        # Kinetic scrolling state
        self.last_y = 0
        self.last_time = 0
        self.velocity = 0
        self.inertia_after_id = None

        # Unique tag for this scroller instance to avoid global interference
        self.tag = f"TouchScroll_{id(self)}"

        self.widget.bind_class(self.tag, "<Button-1>", self._on_press)
        self.widget.bind_class(self.tag, "<B1-Motion>", self._on_drag)
        self.widget.bind_class(self.tag, "<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        # Immediate interruption: cancel any active inertia loop
        self._cancel_inertia()
        
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.dragged = False

        self.last_y = event.y_root
        self.last_time = time.time()
        self.velocity = 0

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

        # Calculate velocity for kinetic scrolling
        now = time.time()
        dt = now - self.last_time
        if dt > 0:
            # Velocity is change in position over change in time
            # We use root coordinates to avoid issues with widget movement
            instant_velocity = (event.y_root - self.last_y) / dt
            # Simple low-pass filter to smooth out noise from small dt
            alpha = 0.5
            self.velocity = (alpha * instant_velocity) + ((1 - alpha) * self.velocity)

        self.last_y = event.y_root
        self.last_time = now

        # Current pointer position
        curr_x = self.widget.winfo_pointerx() - self.widget.winfo_rootx()
        curr_y = self.widget.winfo_pointery() - self.widget.winfo_rooty()

        # Apply axis locking
        if self.lock_axis == 'y':
            curr_x = self.mark_x
        elif self.lock_axis == 'x':
            curr_y = self.mark_y

        self._perform_scroll(curr_x, curr_y)

        # Return "break" to prevent default widget behavior (like text selection)
        # while the user is attempting to scroll.
        return "break"

    def _on_release(self, event):
        if self.dragged:
            # Check if the drag was recent to prevent inertia after holding still (HLP-058)
            if time.time() - self.last_time > 0.1:
                self.velocity = 0

            # Start kinetic scrolling if velocity is significant (HLP-057, HLP-058)
            if abs(self.velocity) > 100:  # Threshold for "fast" drag
                # IMPORTANT: Reset the mark to the CURRENT position so inertia
                # starts from where the finger was released, preventing the "jump back".
                curr_x = self.widget.winfo_pointerx() - self.widget.winfo_rootx()
                curr_y = self.widget.winfo_pointery() - self.widget.winfo_rooty()

                # Update mark coordinates, respecting axis locking
                if self.lock_axis != 'y':
                    self.mark_x = curr_x
                if self.lock_axis != 'x':
                    self.mark_y = curr_y

                self.widget.scan_mark(self.mark_x, self.mark_y)
                self._start_inertia()
            return "break"  # Suppress the click/release action if we dragged
        return None

    def _perform_scroll(self, x, y):
        """Executes the scan_dragto command with safety fallbacks."""
        # tk.Text and tk.Listbox do not support the 'gain' argument in the Python 
        # tkinter wrapper, defaulting to 10x speed. We use tk.call to force gain=1.
        try:
            self.widget.scan_dragto(x, y, gain=1)
        except (tk.TclError, TypeError):
            try:
                self.widget.tk.call(self.widget._w, 'scan', 'dragto', x, y, 1)
            except Exception:
                # Fallback to standard if direct call fails
                self.widget.scan_dragto(x, y)

    def _start_inertia(self):
        """Initiates the kinetic scrolling loop."""
        if abs(self.velocity) < self.min_velocity:
            self.velocity = 0
            return

        # Decay velocity
        self.velocity *= self.friction

        # Calculate new position delta
        # Using a small fixed dt for the after() loop (e.g., 16ms for ~60fps)
        dt = 0.016
        dy = int(self.velocity * dt)

        if dy != 0:
            # Check boundaries (HLP-060)
            # yview() returns (top, bottom) as fractions of total content
            try:
                top, bottom = self.widget.yview()
                if (dy > 0 and top <= 0) or (dy < 0 and bottom >= 1.0):
                    # Hard stop at boundaries (HLP-061)
                    self.velocity = 0
                    return
            except (AttributeError, tk.TclError):
                pass  # Widget might not support yview()

            # Perform the scroll by moving the mark
            # scan_dragto works relative to the mark set by scan_mark
            self.mark_y += dy
            self._perform_scroll(self.mark_x, self.mark_y)

            self.inertia_after_id = self.widget.after(16, self._start_inertia)
        else:
            self.velocity = 0

    def _cancel_inertia(self):
        """Stops any active kinetic scrolling loop."""
        if self.inertia_after_id:
            self.widget.after_cancel(self.inertia_after_id)
            self.inertia_after_id = None
        self.velocity = 0

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
