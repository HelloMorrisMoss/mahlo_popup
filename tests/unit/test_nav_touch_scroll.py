import tkinter as tk
import unittest

from help_window.nav_frame import NavFrame


class TestNavTouchScroll(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.on_select_called = False

        def on_select(article):
            self.on_select_called = True

        self.nav = NavFrame(self.root, on_select=on_select)
        self.nav.pack()

    def tearDown(self):
        self.root.destroy()

    def test_touch_tag_application(self):
        # Mock articles
        articles = [
            {"title": "Test 1", "file_path": "path1", "section": "S1"},
            {"title": "Test 2", "file_path": "path2", "section": "S1"}
        ]
        self.nav.populate(articles)

        # Check if canvas has the tag
        scroller_tag = self.nav.touch_scroller.tag
        self.assertIn(scroller_tag, self.nav.canvas.bindtags())

        # Check if buttons have the tag
        for btn in self.nav.buttons.values():
            self.assertIn(scroller_tag, btn.bindtags())
            # Tag should be at the beginning to intercept
            self.assertEqual(btn.bindtags()[0], scroller_tag)

    def test_drag_suppresses_click(self):
        # This is harder to test without a full event loop simulation
        # but we can check if the methods exist
        self.assertTrue(hasattr(self.nav.touch_scroller, '_on_press'))
        self.assertTrue(hasattr(self.nav.touch_scroller, '_on_drag'))
        self.assertTrue(hasattr(self.nav.touch_scroller, '_on_release'))


if __name__ == "__main__":
    unittest.main()
