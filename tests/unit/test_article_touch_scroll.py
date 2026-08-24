import tkinter as tk
import unittest
from tkinter import ttk

from help_window.article_viewer import ArticleViewer


class TestArticleTouchScroll(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.article_viewer = ArticleViewer(self.root)
        self.article_viewer.pack()

    def tearDown(self):
        self.root.destroy()

    def test_touch_tag_application_text(self):
        # Check if text area has the tag
        scroller_tag = self.article_viewer.touch_scroller.tag
        self.assertIn(scroller_tag, self.article_viewer.text_area.bindtags())

        # Check selection properties
        self.assertFalse(self.article_viewer.text_area.cget("exportselection"))
        bg = self.article_viewer.text_area.cget("background")
        self.assertEqual(str(self.article_viewer.text_area.cget("selectbackground")), str(bg))

    def test_touch_tag_application_media(self):
        # Mock data for image and video
        article_data = [
            {"type": "image", "content": "test.png"},
            {"type": "video", "content": "test.mp4"}
        ]

        # We need to mock path existence to avoid errors during add_image/add_video
        from unittest.mock import patch

        with patch('os.path.isfile', return_value=True):
            with patch('help_window.article_viewer.HelpImage') as mock_img:
                with patch('help_window.article_viewer.HelpVideoPlayer') as mock_vid:
                    # Setup mock widgets
                    img_inst = tk.Frame(self.article_viewer.text_area)
                    img_inst.update_display_size = lambda w: None

                    vid_inst = tk.Frame(self.article_viewer.text_area)
                    vid_inst.update_display_size = lambda w: None

                    # Add a child scale to video to test exclusion
                    scale = ttk.Scale(vid_inst)

                    mock_img.return_value = img_inst
                    mock_vid.return_value = vid_inst

                    self.article_viewer.load_article("Test", article_data)

                    scroller_tag = self.article_viewer.touch_scroller.tag

                    # Check tags
                    self.assertIn(scroller_tag, img_inst.bindtags())
                    self.assertIn(scroller_tag, vid_inst.bindtags())

                    # Check exclusion of Scale
                    self.assertNotIn(scroller_tag, scale.bindtags())


if __name__ == "__main__":
    unittest.main()
