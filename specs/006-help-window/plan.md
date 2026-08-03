# Implementation Plan: Dynamically Configurable Help Window

**Branch**: `feature/help-window` | **Date**: 2026-07-17 | **Spec**: [specs/006-help-window/spec.md]

**Propagated**: 2026-07-21 — Added multi-process integration and Flask signaling.
**Propagated**: 2026-07-22 — Implemented mandatory title block and updated editor to enforce it.
**Propagated**: 2026-07-24 — Added web-based article editor implementation details.
**Propagated**: 2026-08-03 — Added content synchronization, versioning, and headless mode implementation details.

## Summary

The help window is a standalone Tkinter-based component designed for industrial touchscreens. it provides dynamically
loaded, searchable, and cached help content from JSON templates, supporting mixed text, images, and inter-article links.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Tkinter, Azure ttk theme, JSON (for templates), SQLAlchemy (for versioning)

**Storage**: Local JSON cache for help article metadata and content paths; SQLite/PostgreSQL for versioning database.

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
├── help_content/        # Directory for JSON article templates
└── flask_server_files/  # Web editor and synchronization API
    ├── flask_app.py
    ├── models/          # Database models (Versioning)
    ├── static/
    └── templates/
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
   * **Media Scaling**:
       * **Responsive Scaling**: Implement logic to ensure all media fits within the `ArticleViewer` width, overriding
         explicit metadata if necessary to prevent overflow.
       * Images will be resized using `Pillow` while maintaining the aspect ratio.
       * Videos will be resized using `tkVideoPlayer.set_size()`.
       * **Metadata Support**: Parse optional JSON metadata: `size` presets (`thumbnail` to `fill`), static `width`/
         `height`, or `width_pct`.
       * Responsive resizing will be handled via the `<Configure>` event of the `ArticleViewer`.
6. **Window Management**:
    * Implements `<FocusOut>` event binding to either close or stay open.
    * "Stay on Top" toggle using `root.attributes("-topmost", True)`.
7. **Article Editor & Management**:
    * **EditorManager**: Provides a file system view for managing help content.
        * Supports Renaming/Moving files and folders.
        * Automatic reference updates in all articles when paths change.
    * **ArticleEditor**: Block-based editor for article content.
        * Live preview in the main help window.
        * **Media Consolidation**: Logic to pull referenced media into the article's category-specific folder.
8. **Configurable Editor Access**:
    * Adds an `enable_editor` flag to `HelpFrame` and `HelpApp`.
    * If `False` (default), the "Edit Content" button is hidden to prevent operator confusion.
9. **Multi-process Integration & Signaling**:
    * **MainWindow Launcher**: Adds a "Help" button to `MainWindow.py` (Control Panel). Uses `subprocess.Popen` to
      launch `run_help.py`.
    * **Single Instance Enforcement**: `HelpApp` uses a file-based lock (`help_window.lock`) or socket to detect
      running instances.
    * **Flask Signaling**: `HelpApp` starts a minimal Flask server on a dedicated port (e.g., 5005).
      Subsequent launch attempts will send a GET request to `localhost:5005/bring_to_front` before exiting.
    * **Focus Management**: Upon receiving the signal, the existing `HelpApp` calls `lift()` and `focus_force()`
      to appear on top of the full-screen HMI.
10. **Web-based Article Editor**:
    * **Single-Page Application (SPA)**: Implemented using Flask, Jinja2 templates, and vanilla JavaScript (or a
      lightweight framework if needed).
    * **Three-Pane Layout**:
        * **Navigation Pane**: Mirrors the Tk `EditorManager`. Shows a hierarchical view of folders and articles.
          Supports folder creation, moving articles, and media management. Media folders display item counts.
        * **Editor Pane**: Mirrors the Tk `ArticleEditor`.
            * Toolbar includes 'Save', 'Cancel', and 'Consolidate Media' buttons.
            * Block creation via horizontal row of specific buttons (Title, Header, etc.).
            * 'Link' blocks include an article selector dialog.
        * **Preview Pane**: Best-effort WYSIWYG rendering of the article blocks using CSS styles that match the Tk
          `ArticleViewer` appearance.
    * **Modal Dialogs**: Implemented for folder and media management.
        * Selecting a folder or the media directory triggers a modal overlay that dims and disables the main panes.
        * Selection state is managed to revert to the active article upon closing the modal.
    * **Shared Backend**: Reuses `ContentManager` and `FileManager` logic via Flask routes to ensure consistency between
      the Tk and web interfaces.
    * **Media Upload**: Uses standard HTML file inputs to handle media imports into the designated folders.
11. **Content Synchronization & Versioning**:
    * **Role Designation**: Server vs. Subscriber role defined in `untracked_config/settings.json`.
    * **Headless Mode Support**: `run_help.py` supports a GUI-less mode for server instances to host the distribution
      API
      and web editor.
    * **Versioning System**: SQLAlchemy-backed management of content versions, including manifests, SHA-256 hashes, and
      publication status.
    * **CAS Distribution**: Content-Addressable Storage for blobs, enabling deduplication and integrity verification.
    * **Atomic Update Lifecycle**: Background download to staging -> Full integrity check -> Atomic switch to production
      content.
    * **Exponential Backoff**: Subscribers implement backoff for retries when the server is unreachable, failing
      silently
      to the operator.
    * **Management UI**: Separate web page with Basic Auth for creating, inspecting (diffs), and publishing versions.
