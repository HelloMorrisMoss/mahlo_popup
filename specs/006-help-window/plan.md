# Implementation Plan: Dynamically Configurable Help Window

**Branch**: `feature/help-window` | **Date**: 2026-07-17 | **Spec**: [specs/006-help-window/spec.md]

**Propagated**: 2026-07-20 — Updated from spec.md refinement

## Summary

The help window is a standalone Tkinter-based component designed for industrial touchscreens. it provides dynamically
loaded, searchable, and cached help content from JSON templates, supporting mixed text, images, and inter-article links.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Tkinter, Azure ttk theme, JSON (for templates)

**Storage**: Local JSON cache for help article metadata and content paths.

**Testing**: unittest (unit tests for article loading and caching logic), Manual verification for UI behavior.

**Target Platform**: Windows Desktop (Industrial PC)

**Project Type**: desktop-app / widget

**Performance Goals**: < 500ms initial load time (using cache).

**Constraints**: Must be operable with safety gloves (large touch targets).

## Constitution Check

- [ ] Pythonic snake_case for files and methods.
- [ ] Decoupled from `main_window.py` for standalone testing/running.
- [ ] Azure theme styling applied for consistency.

## Project Structure

### Documentation (this feature)

```text
specs/006-help-window/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code

```text
help_window/             # New directory for the help window component
├── __init__.py
├── help_app.py          # Entry point for standalone execution
├── help_frame.py        # Main UI container
├── nav_frame.py         # Navigation list component
├── content_manager.py   # logic for loading, caching, and background updates
└── help_content/        # Directory for JSON article templates
```

## Implementation Details

1. **Standalone Entry Point (`help_app.py`)**: A simple Tkinter app that instantiates `HelpFrame` and handles the main
   loop.
2. **Article Loading Logic (`content_manager.py`)**:
    * Scans `help_content/` directory recursively.
    * Parses JSON templates (title, type, path).
    * Handles errors gracefully (identifies broken templates).
    * Implements caching of the article list to `help_cache.json`.
3. **Background Update Mechanism**:
    * A background thread (or `after()` loop) periodically checks file modification times in `help_content/`.
    * If changes detected, sets a flag and prepares an updated cache.
    * UI shows a subtle "Update Available" button if the flag is set.
4. **Navigation Frame (`nav_frame.py`)**:
    * Uses a `ttk.Treeview` or a custom list of large buttons for touchscreen friendliness.
    * Groups articles by their containing folder (section headers).
5. **Article Viewer Integration**:
   * Adapts the existing `ArticleViewer` widget to support internal links and embedded videos.
    * Links will use a custom tag in `tk.Text` that triggers a navigation event.
   * Videos will be embedded as a new block type using `tk.Text.window_create`.
   * Initial implementation will use `tkVideoPlayer` for native integration, with a modular design to allow a VLC-based
     backend if needed for performance.
6. **Window Management**:
    * Implements `<FocusOut>` event binding to either close or stay open.
    * "Stay on Top" toggle using `root.attributes("-topmost", True)`.
