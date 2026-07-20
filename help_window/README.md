# Help Window System

A standalone, dynamically configurable help system designed for industrial HMI touchscreens.

## Overview

The Help Window is built to provide operators with easy access to documentation and instructions while operating
equipment. It features a touchscreen-friendly interface with safety-glove compatible controls and a flexible,
template-based content system.

## Key Features

- **Industrial UI**: Large buttons and scrollable navigation optimized for touchscreens.
- **Dynamic Content**: Articles are defined in simple JSON templates (located in `help_content/`).
- **Template-Based**: Supports mixed text, images, and inter-article linking.
- **Background Caching**: Automatically caches metadata for near-instant startup.
- **Auto-Update Detection**: Monitors the content directory in the background and notifies the operator if new articles
  are available.
- **Window Management**:
    - **Stay Open / On Top**: Toggle to keep the window always visible while following instructions.
    - **Auto-Close**: When "Stay Open" is disabled, the window automatically closes when it loses focus.
    - **Resizable Layout**: Uses a paned window for flexible side-by-side viewing.

## Directory Structure

- `help_app.py`: Standalone entry point for the Help application.
- `help_frame.py`: Main container orchestrating navigation, viewer, and controls.
- `content_manager.py`: Logic for scanning JSON templates, metadata extraction, and caching.
- `nav_frame.py`: Sidebar listing articles grouped by folder (section).
- `article_viewer.py`: Component for rendering article content (text/images).
- `help_content/`: Directory containing JSON article templates.

## Adding Content

To add a new article:

1. Create a `.json` file in `help_content/` (or a subfolder for organization).
2. Follow the template structure (a list of content blocks):
   ```json
   [
     {"type": "header", "content": "My Article"},
     {"type": "paragraph", "content": "Some description here."},
     {"type": "image", "content": "path/to/image.png"},
     {"type": "link", "content": "Click for More", "target": "other_article.json"}
   ]
   ```
3. The system will automatically detect and include the new article on next launch (or via the background update
   notification).

## Running Standalone

For manual testing or inspection, run the application from the project root:

```bash
python run_help.py
```

Or directly from the `help_window` directory:

```bash
python help_window/help_app.py
```
