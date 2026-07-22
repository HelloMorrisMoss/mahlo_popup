import tkinter as tk
import unittest

from help_window.article_viewer import ArticleViewer
from help_window.utils.article_processor import process_article_data


class TestTitleRedundancy(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.viewer = ArticleViewer(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_header_shows_in_text_area(self):
        """
        Verify that currently, a 'header' block shows up in the text area,
        causing redundancy if it's also used as the window title.
        """
        article_data = [
            {"type": "header", "content": "My Redundant Title"},
            {"type": "paragraph", "content": "Some content."}
        ]

        process_article_data(self.viewer, "My Redundant Title", article_data)

        # Check title_var
        self.assertEqual(self.viewer.title_var.get(), "My Redundant Title")

        # Check text area content
        content = self.viewer.text_area.get("1.0", "end")
        self.assertIn("My Redundant Title", content)

    def test_new_title_block_behavior(self):
        """
        Verify that 'title' block sets the window title but does NOT show in text area.
        """
        article_data = [
            {"type": "title", "content": "My Clean Title"},
            {"type": "paragraph", "content": "Some content."}
        ]

        # We pass an argument title, but the 'title' block should override it
        process_article_data(self.viewer, "Argument Title", article_data)

        # Check title_var - it should be from the block
        self.assertEqual(self.viewer.title_var.get(), "My Clean Title")

        content = self.viewer.text_area.get("1.0", "end")
        # It should NOT be in the text area
        self.assertNotIn("My Clean Title", content)
        self.assertIn("Some content.", content)


if __name__ == "__main__":
    unittest.main()
