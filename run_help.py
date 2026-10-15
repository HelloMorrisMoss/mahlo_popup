import argparse
import os
import sys

# Add the project root to sys.path to ensure absolute imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from help_window.help_app import run_standalone, run_headless
from help_window.utils.config import set_role_override

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Mahlo Help System")
    parser.add_argument("--headless", action="store_true", help="Run without GUI (server only)")
    parser.add_argument("--editor", action="store_true", default=True, help="Enable editor features")
    parser.add_argument("--port", type=int, help="Override the Flask API port")
    parser.add_argument("--server-url", type=str, help="Override the content server URL (for subscribers)")
    parser.add_argument("--role", type=str, choices=["server", "subscriber"], help="Override the instance role")
    parser.add_argument("--content-dir", type=str, help="Override the help content directory")

    args = parser.parse_args()

    if args.role:
        set_role_override(args.role)

    if args.headless:
        print(
            f"Launching Help System in HEADLESS mode (Role: {args.role or 'default'}) on port {args.port or 'default'}.")
        run_headless(port=args.port, content_dir=args.content_dir)
    else:
        print(f"Launching Help Window (Role: {args.role or 'default'}) on port {args.port or 'default'}.")
        run_standalone(enable_editor=args.editor, port=args.port, server_url=args.server_url,
                       content_dir=args.content_dir)
