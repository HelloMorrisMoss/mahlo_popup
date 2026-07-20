# Tasks: Dynamically Configurable Help Window

**Input**: Design documents from `/specs/006-help-window/`

**Propagated**: 2026-07-20 — Refined media scaling and metadata tasks for consistency with spec.md.

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
