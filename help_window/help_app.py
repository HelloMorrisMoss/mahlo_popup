import os
import sys
import threading
import tkinter as tk

import requests

from help_window.flask_server_files.flask_app import start_flask_server
from untracked_config.configuration_data import help_api_port

# Add parent directory to sys.path to allow importing from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dev_common import style_component
from help_window.help_frame import HelpFrame
from help_window.content_manager import ContentManager


class HelpApp(tk.Tk):
    """
    Standalone application for the Help Window.
    """

    def __init__(self, enable_editor: bool = False):
        super().__init__()
        self.enable_editor = enable_editor

        self.title("Mahlo Help System")
        self.geometry("1024x768")

        # Initialize Content Manager
        content_dir = os.path.join(os.path.dirname(__file__), "help_content")
        self.content_manager = ContentManager(content_dir)

        # Apply Azure theme
        style_component(self)

        self.help_frame = HelpFrame(self, self.content_manager, enable_editor=self.enable_editor)
        self.help_frame.pack(expand=True, fill="both")

    def bring_to_front(self):
        """Forces the window to the front and focuses it."""
        self.deiconify()
        self.lift()
        self.focus_force()
        # On some windows versions, focus_force isn't enough to come over full screen apps
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False) if not self.help_frame.stay_open_var.get() else None)


def is_already_running():
    """Checks if another instance of the help system is already running via Flask signaling."""
    try:
        response = requests.get(f"http://localhost:{help_api_port}/bring_to_front", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def run_standalone(enable_editor=False):
    """Standard entry point for running the help system as a standalone process."""
    if is_already_running():
        print("Help system is already running. Signaled existing instance to bring to front.")
        sys.exit(0)

    app = HelpApp(enable_editor=enable_editor)

    # Start Flask server in a daemon thread
    flask_thread = threading.Thread(target=start_flask_server, args=(app,), daemon=True)
    flask_thread.start()

    app.mainloop()


if __name__ == "__main__":
    run_standalone()
