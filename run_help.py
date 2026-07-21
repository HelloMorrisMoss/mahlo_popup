import os
import sys

# Add the project root to sys.path to ensure absolute imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from help_window.help_app import run_standalone

if __name__ == "__main__":
    print("Launching Help Window for article editing.")
    run_standalone(enable_editor=True)
