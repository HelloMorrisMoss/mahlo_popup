import tkinter as tk
import unittest

from help_window.editor.article_editor import ArticleEditor


class TestEditorLogic(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()

    def tearDown(self):
        self.root.destroy()

    def test_ensure_title_block_missing(self):
        """Verify that ArticleEditor adds a title block if missing."""
        initial_data = [
            {"type": "header", "content": "My Header"},
            {"type": "paragraph", "content": "Some text."}
        ]
        # We don't need a real file_path or on_save for this test if we don't call save()
        editor = ArticleEditor(self.root, initial_data, "Test Title", "dummy.json", None)

        # The first block should now be a title block
        self.assertEqual(editor.blocks[0]["type"], "title")
        self.assertEqual(editor.blocks[0]["content"], "My Header")  # It should have converted the header
        self.assertEqual(len(editor.blocks), 2)

    def test_ensure_title_block_added(self):
        """Verify that ArticleEditor adds a title block if no header/title exists."""
        initial_data = [
            {"type": "paragraph", "content": "Some text."}
        ]
        editor = ArticleEditor(self.root, initial_data, "Test Title", "dummy.json", None)

        self.assertEqual(editor.blocks[0]["type"], "title")
        self.assertEqual(editor.blocks[0]["content"], "Test Title")
        self.assertEqual(len(editor.blocks), 2)

    def test_ensure_title_block_already_exists(self):
        """Verify that ArticleEditor doesn't duplicate title block."""
        initial_data = [
            {"type": "title", "content": "Existing Title"},
            {"type": "paragraph", "content": "Some text."}
        ]
        editor = ArticleEditor(self.root, initial_data, "Test Title", "dummy.json", None)

        self.assertEqual(editor.blocks[0]["type"], "title")
        self.assertEqual(editor.blocks[0]["content"], "Existing Title")
        self.assertEqual(len(editor.blocks), 2)


if __name__ == "__main__":
    unittest.main()
