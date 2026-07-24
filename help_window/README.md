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

## Content Management & Editing

The help system includes two primary ways to manage and edit articles:

### 1. Desktop Article Editor (Tkinter)

The desktop editor is built directly into the help application. It provides a full-featured interface for creating,
modifying, and reordering content blocks.

- **To Launch**: Run `python run_help.py` from the project root.
- **Best For**: High-intensity editing on a computer with a physical keyboard.
- **Key Features**: Direct filesystem access, block properties management, and integrated media selection.

### 2. Web Article Editor (Flask SPA)

A modern, single-page web interface that allows remote content management without requiring the user to be at the Mahlo
HMI.

- **To Access**: Ensure the help system is running, then navigate to `http://<machine-ip>:5005/editor` in any modern web
  browser.
- **Best For**: Remote documentation updates, quick fixes, and collaborative editing.
- **Key Features**: Three-pane layout (Navigation, Editor, Preview), drag-and-drop block management, and folder/media
  management.

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
     {"type": "title", "content": "My Article"},
     {"type": "paragraph", "content": "Some description here."},
     {"type": "header", "content": "Section 1"},
     {"type": "image", "content": "path/to/image.png", "size": "medium"},
     {"type": "video", "content": "path/to/video.mp4", "width_pct": 80},
     {"type": "link", "content": "Click for More", "target": "other_article.json"}
   ]
   ```

### Block Types

- `title`: **Required.** Exactly one per article, must be the first block. Used for navigation and window title.
- `header`: Large bold text.
- `subheader`: Medium bold text.
- `paragraph`: Standard text content.
- `image`: Displays an image.
- `video`: Embeds a video player.
- `link`: Clickable link to another help article.
- `separator`: Horizontal line.

### Media Metadata

Images and videos support optional metadata for scaling:

- `size`: `thumbnail` (25%), `small` (50%), `medium` (75%), `large` (90%), `fill` (100% of viewer width).
- `width_pct`: Numeric percentage of viewer width (e.g., `80`).
- `width`, `height`: Static dimensions in pixels (e.g., `"1441x1080"` or separate `width`: 400, `height`: 300).

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
