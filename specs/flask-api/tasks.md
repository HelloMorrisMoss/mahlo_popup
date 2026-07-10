# Tasks: Flask REST API

**Input**: Design documents from `/specs/002-flask-api/`

## Phase 1: Setup
- [x] T001 Configure Flask application factory (`flask_app.py`)
- [x] T002 Integrate Flask-Restful and define API resources

## Phase 2: Foundational
- [x] T003 [P] Implement SQLAlchemy integration and shared session handling
- [x] T004 Implement `queuesholder` to share state across requests

## Phase 3: User Story 1 - Defect Management 🎯 MVP
- [x] T005 [P] [US1] Implement `Defect` and `DefectList` resources
- [x] T006 [US1] Implement `Operator` and `Operators` resources

## Phase 4: User Story 2 - UI Signaling via Popups
- [x] T007 [US2] Implement `Popup` resource for UI signaling
- [x] T008 [US2] Implement `ButtonMessage` resource

## Phase 5: User Story 3 - Background Task Management
- [x] T009 [US3] Implement APScheduler integration
- [x] T010 [US3] Create `regular_check_function` for queue processing
- [x] T011 [US3] Implement `check_that_port_is_mine` logic

## Phase N: Polish & Gaps
- [ ] T012 Implement robust API authentication/security
- [ ] T013 Increase unit test coverage for Resource classes
- [ ] T014 Refactor port control logic
