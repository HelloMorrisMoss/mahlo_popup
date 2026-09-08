import sys
import tkinter as tk
import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch

# Mock cv2 before importing the widget if it doesn't exist
if 'cv2' not in sys.modules:
    mock_cv2 = ModuleType('cv2')
    mock_cv2.VideoCapture = MagicMock()
    mock_cv2.COLOR_BGR2RGB = 4
    mock_cv2.cvtColor = MagicMock()
    mock_cv2.CAP_PROP_FPS = 5
    mock_cv2.CAP_PROP_FRAME_COUNT = 7
    mock_cv2.CAP_PROP_FRAME_WIDTH = 3
    mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
    mock_cv2.CAP_PROP_POS_FRAMES = 1
    sys.modules['cv2'] = mock_cv2

from help_window.widgets.video_player import OpenCVVideoPlayer


class TestOpenCVVideoPlayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    @patch('cv2.VideoCapture')
    def test_init_and_scaling(self, mock_vc):
        # Setup mock
        instance = mock_vc.return_value
        instance.isOpened.return_value = True
        instance.read.return_value = (False, None)  # Don't read anything

        def mock_get(prop):
            if prop == 5: return 30.0  # FPS
            if prop == 7: return 300.0  # FRAME_COUNT
            if prop == 3: return 640.0  # WIDTH
            if prop == 4: return 360.0  # HEIGHT
            return 0.0

        instance.get.side_effect = mock_get

        # Test init
        player = OpenCVVideoPlayer(self.root, "dummy.mp4")
        self.assertEqual(player.fps, 30.0)
        self.assertEqual(player.duration, 10.0)

        # Test scaling
        player.update_display_size(1000)
        self.assertEqual(player._target_size[0], 640)  # Original width fits 1000

        player.update_display_size(500)
        self.assertEqual(player._target_size[0], 500)  # Capped at 500

        player.stop()

    @patch('cv2.VideoCapture')
    def test_playback_controls(self, mock_vc):
        instance = mock_vc.return_value
        instance.isOpened.return_value = True
        instance.get.return_value = 30.0
        instance.read.return_value = (False, None)

        player = OpenCVVideoPlayer(self.root, "dummy.mp4")

        # Initially not playing
        self.assertFalse(player._playing)

        # Toggle play
        player.toggle_play()
        self.assertTrue(player._playing)
        self.assertEqual(player.play_btn.cget("text"), "Pause")

        # Toggle again
        player.toggle_play()
        self.assertFalse(player._playing)
        self.assertEqual(player.play_btn.cget("text"), "Play")

        # Stop
        player._playing = True
        player.stop_video()
        self.assertFalse(player._playing)
        self.assertEqual(player.current_frame_idx, 0)

        player.stop()


if __name__ == '__main__':
    unittest.main()
