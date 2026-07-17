import os
import sys
import tkinter as tk

# Add parent directory to sys.path to allow importing from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dev_common import style_component
from help_window.help_frame import HelpFrame
from help_window.content_manager import ContentManager


class HelpApp(tk.Tk):
    """
    Standalone application for the Help Window.
    """

    def __init__(self):
        super().__init__()

        self.title("Mahlo Help System")
        self.geometry("1024x768")

        # Initialize Content Manager
        content_dir = os.path.join(os.path.dirname(__file__), "help_content")
        self.content_manager = ContentManager(content_dir)

        # Apply Azure theme
        style_component(self)

        self.help_frame = HelpFrame(self, self.content_manager)
        self.help_frame.pack(expand=True, fill="both")


if __name__ == "__main__":
    app = HelpApp()
    app.mainloop()
