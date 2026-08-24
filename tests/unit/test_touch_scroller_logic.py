import time
import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from help_window.utils.touch_scroller import TouchScroller


class TestTouchScrollerLogic(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.scroller = TouchScroller(self.canvas)

    def tearDown(self):
        self.root.destroy()

    def test_on_drag_returns_break(self):
        """Verify that drag events return 'break' to suppress default widget behavior."""

        class MockEvent:
            def __init__(self, x, y):
                self.x_root = x
                self.y_root = y

        self.scroller._on_press(MockEvent(100, 100))
        result = self.scroller._on_drag(MockEvent(110, 110))
        self.assertEqual(result, "break", "Drag event must return 'break' to prevent selection")

    def test_dragged_state(self):
        """Verify the dragged state is correctly updated based on threshold."""

        class MockEvent:
            def __init__(self, x, y):
                self.x_root = x
                self.y_root = y

        self.scroller._on_press(MockEvent(100, 100))

        # Move within threshold (default 10)
        self.scroller._on_drag(MockEvent(105, 105))
        self.assertFalse(self.scroller.dragged)

        # Move beyond threshold
        self.scroller._on_drag(MockEvent(115, 115))
        self.assertTrue(self.scroller.dragged)

    def test_interruption_logic(self):
        """Verify that a new press cancels active inertia."""
        self.scroller.inertia_after_id = "after_id_123"
        self.scroller.velocity = 500

        class MockEvent:
            def __init__(self, x, y):
                self.x_root = x
                self.y_root = y

        with patch.object(self.canvas, 'after_cancel') as mock_cancel:
            self.scroller._on_press(MockEvent(100, 100))
            mock_cancel.assert_called_once_with("after_id_123")
            self.assertEqual(self.scroller.velocity, 0)
            self.assertIsNone(self.scroller.inertia_after_id)

    def test_kinetic_start_threshold(self):
        """Verify kinetic scrolling starts only above velocity threshold."""

        class MockEvent:
            def __init__(self, x, y):
                self.x_root = x
                self.y_root = y

        self.scroller.dragged = True
        self.scroller.last_time = time.time()

        # Low velocity
        self.scroller.velocity = 50
        with patch.object(self.scroller, '_start_inertia') as mock_start:
            self.scroller._on_release(MockEvent(100, 100))
            mock_start.assert_not_called()

        # High velocity
        self.scroller.velocity = 200
        self.scroller.last_time = time.time()
        with patch.object(self.scroller, '_start_inertia') as mock_start:
            self.scroller._on_release(MockEvent(100, 100))
            mock_start.assert_called_once()

    def test_boundary_enforcement(self):
        """Verify scrolling stops at content boundaries."""
        self.scroller.velocity = 1000
        self.scroller.mark_y = 500

        # Mock yview to simulate being at the top (top=0.0)
        self.canvas.yview = MagicMock(return_value=(0.0, 0.5))

        # dy = velocity * 0.016 = 16 (positive means scrolling up, top decreasing)
        # In our implementation, dy > 0 means moving finger down, content moves down (top increases)
        # Wait, scan_dragto(..., gain=1) means if we drag finger down, content moves down.
        # If dy > 0 (finger moving down), and top <= 0, we are already at the top.

        with patch.object(self.canvas, 'after') as mock_after:
            self.scroller._start_inertia()
            self.assertEqual(self.scroller.velocity, 0)
            mock_after.assert_not_called()

    def test_on_release_resets_mark(self):
        """Verify that scan_mark is reset on release to prevent jump back."""

        class MockEvent:
            def __init__(self, x, y):
                self.x_root = x
                self.y_root = y

        self.scroller.dragged = True
        self.scroller.velocity = 200
        self.scroller.last_time = time.time()

        with patch.object(self.canvas, 'scan_mark') as mock_scan_mark:
            # We don't strictly need to mock winfo_pointer because we just care it's called
            self.scroller._on_release(MockEvent(100, 100))
            mock_scan_mark.assert_called_once()

    def test_velocity_smoothing(self):
        """Verify that velocity calculation uses smoothing."""

        class MockEvent:
            def __init__(self, x, y, x_root, y_root):
                self.x = x
                self.y = y
                self.x_root = x_root
                self.y_root = y_root

        self.scroller._on_press(MockEvent(10, 10, 100, 100))
        self.scroller.last_time = time.time() - 0.016  # 16ms ago

        # Move 16 pixels in 16ms -> instant velocity = 1000
        # Initial velocity was 0. alpha = 0.5
        # Expected velocity = 0.5 * 1000 + 0.5 * 0 = 500
        self.scroller._on_drag(MockEvent(10, 26, 100, 116))
        self.assertAlmostEqual(self.scroller.velocity, 500, delta=10)


if __name__ == "__main__":
    unittest.main()
