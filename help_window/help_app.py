import os
import sys
import threading
import tkinter as tk

from flask_server_files.helpers import single_instance
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

    def __init__(self, enable_editor: bool = False, server_url: str = None, content_dir: str = None):
        super().__init__()
        self.enable_editor = enable_editor
        self.server_url = server_url

        self.title("Mahlo Help System")
        self.geometry("1024x768")

        # Initialize Content Manager
        if not content_dir:
            content_dir = os.path.join(os.path.dirname(__file__), "help_content")
        self.content_manager = ContentManager(content_dir)

        # Apply Azure theme
        style_component(self)

        self.help_frame = HelpFrame(self, self.content_manager, enable_editor=self.enable_editor,
                                    server_url=self.server_url)
        self.help_frame.pack(expand=True, fill="both")

    def bring_to_front(self):
        """Forces the window to the front and focuses it."""
        self.deiconify()
        self.lift()
        self.focus_force()
        # On some windows versions, focus_force isn't enough to come over full screen apps
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False) if not self.help_frame.stay_open_var.get() else None)


class HeadlessHelpApp:
    """
    Minimal mock of HelpApp for headless (server-only) mode.
    """

    def __init__(self, server_url: str = None, content_dir: str = None):
        if not content_dir:
            content_dir = os.path.join(os.path.dirname(__file__), "help_content")
        self.content_manager = ContentManager(content_dir)
        self.server_url = server_url

    def bring_to_front(self):
        """No-op in headless mode."""
        pass


def is_already_running(port: int = None):
    """Checks if another instance of the help system is already running via Flask signaling."""
    import requests
    target_port = port or help_api_port
    try:
        response = requests.get(f"http://localhost:{target_port}/bring_to_front", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def run_standalone(enable_editor=False, port: int = None, server_url: str = None, content_dir: str = None):
    """Standard entry point for running the help system as a standalone process."""
    # Use different lock files if ports are different to allow concurrent dev instances
    suffix = f"_{port}" if port else ""
    lock_file = os.path.join(os.path.dirname(__file__), f"help_window{suffix}.lock")

    try:
        with single_instance(lock_file, timeout=0.5):
            app = HelpApp(enable_editor=enable_editor, server_url=server_url, content_dir=content_dir)

            # Start Flask server in a daemon thread
            flask_thread = threading.Thread(target=start_flask_server, args=(app, port), daemon=True)
            flask_thread.start()

            app.mainloop()
    except OSError:
        # If lock fails, try to signal existing instance
        if is_already_running(port):
            print(
                f"Help system is already running on port {port or help_api_port}. Signaled existing instance to bring to front.")
        else:
            print("Help system seems to be locked but not responding to signals.")
        sys.exit(0)


def run_headless(port: int = None, content_dir: str = None):
    """Entry point for running the help system without a GUI (headless mode)."""
    suffix = f"_{port}_headless" if port else "_headless"
    lock_file = os.path.join(os.path.dirname(__file__), f"help_window{suffix}.lock")

    try:
        with single_instance(lock_file, timeout=0.5):
            app = HeadlessHelpApp(content_dir=content_dir)

            # Start Flask server (could be in main thread since no Tk loop)
            # But let's keep it in a thread or just run it directly if we want it to block
            start_flask_server(app, port)
    except OSError:
        print(f"Headless help system is already running on port {port or help_api_port}.")
        sys.exit(0)


if __name__ == "__main__":
    run_standalone()
