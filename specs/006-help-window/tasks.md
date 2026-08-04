# Tasks: Dynamically Configurable Help Window

**Input**: Design documents from `/specs/006-help-window/`

**Propagated**: 2026-07-21 — Added tasks for multi-process integration and signaling.
**Propagated**: 2026-07-22 — Added task T030 for title block cleanup and redundancy removal.
**Propagated**: 2026-07-24 — Added tasks for web-based article editor.
**Propagated**: 2026-08-03 — Added tasks for content synchronization, versioning, and headless mode.

## Phase 1: Setup & Infrastructure

- [x] T001 Create `help_window/` directory structure and `help_app.py` skeleton
- [x] T002 Implement `ContentManager` for scanning and parsing JSON templates
- [x] T003 Implement caching logic in `ContentManager`

## Phase 2: UI Foundation

- [x] T004 Create `HelpFrame` with side-by-side layout (nav and content)
- [x] T005 Implement `NavFrame` with folder-based section headers
- [x] T006 Integrate refined `ArticleViewer` into `HelpFrame`

## Phase 3: Dynamic Features & Interaction

- [x] T007 Implement inter-article linking in `ArticleViewer`
- [x] T007.1 Implement video block support in `ArticleViewer` using `tkVideoPlayer`
- [x] T008 Implement window behavior controls (Focus loss behavior, Stay on Top)
- [x] T009 Implement navigation list toggle (show/hide)
- [x] T017 Implement media scaling and metadata support in `ArticleViewer`
  - [x] T017.1 Integrate `Pillow` for image resizing
  - [x] T017.2 Implement dynamic width calculation for images and videos
  - [x] T017.3 Implement metadata parsing for size, dimensions, and percentages
  - [x] T017.4 Implement responsive resizing on window `<Configure>` event

## Phase 4: Background Processing & Polish

- [x] T010 Implement background update check mechanism
- [x] T011 Implement "Update Available" UI notification and auto-caching
- [x] T012 Implement error handling for malformed templates (broken indicator)

## Phase 5: Verification & Documentation

- [x] T013 Create unit tests for `ContentManager` (loading/caching/errors)
- [x] T014 Perform manual verification on touchscreen (if available) or via mouse
- [x] T015 Update `ARCHITECTURE.md` with the new component details
- [x] T016 Create `help_window/README.md` and `run_help.py` entry point

## Phase 6: WYSIWYG Editor & Content Management

- [x] T018 Implement `ArticleEditor` with block management and live preview
- [x] T019 Implement `EditorManager` for file/folder management
- [x] T020 Implement `FileManager` with automatic reference updates for renames
- [x] T021 Implement "Move to Folder" functionality in `EditorManager`
- [x] T022 Implement "Consolidate Media" functionality in `ArticleEditor`
- [x] T023 Verify all content management features with integration tests
- [x] T024 Implement configurable "Edit Content" button (HLP-024)

## Phase 7: Multi-process Integration & Main Window UI

- [x] T025 Add "Help" button to `MainWindow.py` control panel (after operator grid button)
- [x] T026 Implement subprocess launcher in `MainWindow.py` to call `run_help.py`
- [x] T027 Implement file-based instance lock in `HelpApp`
- [x] T028 Implement minimal Flask server with `/bring_to_front` endpoint in `HelpApp`
- [x] T029 Implement signaling logic in `HelpApp` (send request to Flask before exiting if instance exists)
- [x] T030 Clean up article titles and implement mandatory title block (HLP-029)
  - [x] T030.1 Implement `title` block type in `ContentManager` and `ArticleViewer`
  - [x] T030.2 Update `ArticleEditor` to enforce mandatory title block rules
  - [x] T030.3 Migrate all existing articles to use `title` block
  - [x] T030.4 Update documentation in `help_window/README.md`

## Phase 8: Web-based Article Editor

- [x] T031 [US9] Design and implement Flask routes for the web editor in help_window/flask_server_files/flask_app.py (
  HLP-030)
- [x] T032 [US9] Create three-pane layout templates in help_window/flask_server_files/templates/web_editor.html (
  HLP-031)
- [x] T033 [US9] Implement Navigation pane logic in help_window/flask_server_files/static/web_editor.js (HLP-032)
- [x] T034 [US9] Implement Editor pane logic in help_window/flask_server_files/static/web_editor.js (HLP-033)
- [x] T035 [US9] Implement Preview pane with best-effort WYSIWYG rendering in
  help_window/flask_server_files/static/web_editor.js (HLP-034)
- [x] T036 [US9] Integrate existing ContentManager and file system utilities (HLP-035)
- [x] T037 [US9] Verify web editor functionality with integration tests in tests/integration/test_web_editor.py

## Phase 9: Web-based Article Editor Enhancements (HLP-032 to HLP-036)

- [x] T038 [US9] Enhance Navigation Pane:
  - [x] T038.1 [US9] Implement hierarchical folder/article view (HLP-032.1)
  - [x] T038.2 [US9] Implement folder creation and item moving (HLP-032.2, HLP-032.3)
  - [x] T038.3 [US9] Implement 'media' folder with item count (HLP-032.4)
- [x] T039 [US9] Enhance Editor Pane UI:
  - [x] T039.1 [US9] Add 'Save', 'Cancel', and 'Consolidate Media' buttons (HLP-033.2)
  - [x] T039.2 [US9] Replace '+ Add Block' with horizontal button row (HLP-033.3)
  - [x] T039.3 [US9] Implement 'Link' block article selector (HLP-033.4)
- [x] T040 [US9] Implement Modal Floating Windows in help_window/flask_server_files/static/web_editor.js:
  - [x] T040.1 [US9] Implement modal overlay system (dim/disable panes) (HLP-036.3)
  - [x] T040.2 [US9] Implement Media Browser modal (HLP-036.1)
  - [x] T040.3 [US9] Implement Folder Management modal (HLP-036.2)
  - [x] T040.4 [US9] Implement selection reversion logic (HLP-036.4)
- [x] T041 [US9] Verify enhancements with updated tests

## Phase 10: Content Synchronization & Versioning

- [x] T042 [US10] Implement Headless Mode in run_help.py (HLP-050)
- [x] T043 [US10] Implement Server/Subscriber role detection from untracked_config/settings.json (HLP-037)
- [x] T044 [US10] Define SQLAlchemy Database Schema for Versioning in
  help_window/flask_server_files/models/version.py (HLP-049)
- [x] T045 [US10] Implement CAS Storage and Manifest Generation Logic in help_window/utils/cas_manager.py (HLP-040,
  HLP-048)
- [x] T046 [US10] Implement Versioning Management Web UI in help_window/flask_server_files/templates/versioning.html (
  HLP-043 to HLP-047)
  - [x] T046.1 [US10] Implement version creation and history view
  - [x] T046.2 [US10] Implement change inspection (text diffs and media previews)
  - [x] T046.3 [US10] Implement manual publication logic
- [x] T047 [US10] Implement Subscriber Sync Logic (polling server) with Exponential Backoff in
  help_window/content_manager.py (HLP-038,
  HLP-039)
- [x] T048 [US10] Implement Subscriber-side Content Verification (Full Integrity Check) in
  help_window/content_manager.py (HLP-040)
- [x] T049 [US10] Implement Atomic Content Switch on Subscriber in help_window/editor/file_manager.py (HLP-040, HLP-041,
  HLP-051):
  - [x] T049.1 [US10] Implement directory swap/switch logic
  - [x] T049.2 [US10] Implement "New version available - Refresh" notification in UI
- [x] T050 [US10] Implement Basic Auth for Versioning Management interface in
  help_window/flask_server_files/flask_app.py (HLP-043)
- [x] T051 [US10] Verify Synchronization and Rollback with Integration Tests in tests/integration/test_sync.py (SC-007,
  SC-008)

## Phase 11: Development & Test Support

- [x] T052 [US10] Implement CLI overrides for Port, Server URL, and Role in run_help.py and help_app.py to support
  multi-instance testing (HLP-052)
- [x] T053 [US10] Implement regression test `tests/unit/test_sync_hash_bug.py` for manifest hash stability
- [x] T054 [US10] Implement regression test `tests/unit/test_help_frame_refresh.py` for UI reload persistence
- [x] T055 [US10] Implement regression test `tests/unit/test_content_manager_bug.py` for file exclusion logic
