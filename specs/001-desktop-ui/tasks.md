# Tasks: Desktop UI (Tkinter)

**Propagated**: 2026-07-16 — Updated from spec.md refinement (Refined "Always on Top" functionality).

**Input**: Design documents from `/specs/001-desktop-ui/`

## Phase 1: Setup
- [x] T001 Initialize Tkinter project with Azure theme resources

## Phase 2: Foundational
- [x] T002 Set up Tkinter main window structure (`main_window.py`)
- [x] T003 [P] Implement thread-safe queue polling mechanism

## Phase 3: User Story 1 - Defect Logging 🎯 MVP
- [x] T004 [P] [US1] Develop custom defect logging buttons in `widgets/`
- [x] T005 [US1] Bind button events to outbound queue

## Phase 4: User Story 2 - Real-time Messaging
- [x] T006 [US2] Implement message processing from inbound queue
- [x] T007 [US2] Create system alert display logic in `msg_window/`

## Phase 5: User Story 3 - Window Management
- [x] T008 [US3] Implement window position persistence
- [x] T009 [US3] Implement "Always on Top" functionality (refined to prevent taskbar activation via win32gui)

## Phase N: Polish & Gaps
- [ ] T010 Add unit tests for custom widgets logic
- [ ] T011 Implement UI integration tests
- [ ] T012 Document internal queue message format schema

## Phase 6: Extended Controls (Update 2026-07-14)

- [x] T013 [US6] Add "Clear Old Records" button with `marked_for_deletion` logic
- [x] T014 [US7] Implement multi-click system restart button with email notification
- [x] T015 [US7] Rename original restart button to "Restart Popup"
- [x] T016 [US8] Create `OperatorGridWindow` with flex-fill grid and headers
- [x] T017 [US8] Add grid selection trigger to `IndependentControlsPanel`
- [x] T018 [US7] Refine system restart to use `SystemRestartError` and top-level context-rich notifications
