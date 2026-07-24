# Tasks: Dynamically Configurable Help Window

**Input**: Design documents from `/specs/006-help-window/`

**Propagated**: 2026-07-21 — Added tasks for multi-process integration and signaling.
**Propagated**: 2026-07-22 — Added task T030 for title block cleanup and redundancy removal.
**Propagated**: 2026-07-24 — Added tasks for web-based article editor.

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

- [x] T031 Design and implement Flask routes for the web editor (HLP-030)
- [x] T032 Create three-pane layout templates (Navigation, Editor, Preview) (HLP-031)
- [x] T033 Implement Navigation pane logic (Article/Folder management, Media import) (HLP-032)
- [x] T034 Implement Editor pane logic (Block management mirroring Tk editor) (HLP-033)
- [x] T035 Implement Preview pane with best-effort WYSIWYG rendering (HLP-034)
- [x] T036 Integrate existing `ContentManager` and file system utilities (HLP-035)
- [x] T037 Verify web editor functionality with integration tests

## Phase 9: Web-based Article Editor Enhancements (HLP-032 to HLP-036)

- [ ] T038 Enhance Navigation Pane:
  - [ ] T038.1 Implement hierarchical folder/article view (HLP-032.1)
  - [ ] T038.2 Implement folder creation and item moving (HLP-032.2, HLP-032.3)
  - [ ] T038.3 Implement 'media' folder with item count (HLP-032.4)
- [ ] T039 Enhance Editor Pane UI:
  - [ ] T039.1 Add 'Save', 'Cancel', and 'Consolidate Media' buttons (HLP-033.2)
  - [ ] T039.2 Replace '+ Add Block' with horizontal button row (HLP-033.3)
  - [ ] T039.3 Implement 'Link' block article selector (HLP-033.4)
- [ ] T040 Implement Modal Floating Windows:
  - [ ] T040.1 Implement modal overlay system (dim/disable panes) (HLP-036.3)
  - [ ] T040.2 Implement Media Browser modal (HLP-036.1)
  - [ ] T040.3 Implement Folder Management modal (HLP-036.2)
  - [ ] T040.4 Implement selection reversion logic (HLP-036.4)
- [ ] T041 Verify enhancements with updated tests
