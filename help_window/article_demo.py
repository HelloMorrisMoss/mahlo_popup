import json
import os
import sys
import tkinter as tk
from tkinter import ttk

# Add project root to path so we can import widgets
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from help_window.article_viewer import ArticleViewer
from dev_common import style_component


def create_demo_json(filepath):
    """Creates a sample article JSON file."""
    data = [
        {"type": "header", "content": "Operator Documentation"},
        {"type": "paragraph",
         "content": "Welcome to the Mahlo Popup system documentation. This guide covers basic operations and troubleshooting."},
        {"type": "subheader", "content": "Main Interface"},
        {"type": "image", "content": "explorer_mXEOC0cuqq.png"},
        {"type": "paragraph",
         "content": "The main window stays on top of other applications to ensure you can always log defects quickly."},
        {"type": "separator", "content": ""},
        {"type": "subheader", "content": "Logging a Defect"},
        {"type": "paragraph",
         "content": "1. Identify the defect on the line.\n2. Click the corresponding button in the popup.\n3. The record will be saved to the database automatically."},
        {"type": "paragraph",
         "content": "Note: If you made a mistake, you can use the 'Clear Old Records' button in the settings menu."}
    ]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def run_demo():
    root = tk.Tk()
    root.title("Mahlo Article Viewer Demo")
    root.geometry("800x600")

    # Apply project style (Azure theme)
    try:
        style_component(root, project_root)
    except Exception as e:
        print(f"Could not apply style: {e}")

    # Main container
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(expand=True, fill="both")

    # Left side: Article list (mockup)
    list_frame = ttk.LabelFrame(main_frame, text="Articles", padding=5)
    list_frame.pack(side="left", fill="y", padx=(0, 10))

    # Right side: Article viewer
    viewer_frame = ttk.LabelFrame(main_frame, text="Content", padding=5)
    viewer_frame.pack(side="right", expand=True, fill="both")

    viewer = ArticleViewer(viewer_frame)
    viewer.pack(expand=True, fill="both")

    # Sample data
    demo_file = "sample_article.json"
    create_demo_json(demo_file)

    def load_selected():
        with open(demo_file, 'r') as f:
            article_data = json.load(f)
        viewer.load_article("Demo Article", article_data)

    # Load button
    load_btn = ttk.Button(list_frame, text="Load Operator Guide", command=load_selected)
    load_btn.pack(pady=5, fill="x")

    # Clear button
    clear_btn = ttk.Button(list_frame, text="Clear", command=viewer.clear)
    clear_btn.pack(pady=5, fill="x")

    # Initial load
    load_selected()

    root.mainloop()

    # Cleanup
    if os.path.exists(demo_file):
        os.remove(demo_file)


if __name__ == "__main__":
    run_demo()
