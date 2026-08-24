import tkinter as tk
import unittest

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


if __name__ == "__main__":
    unittest.main()
