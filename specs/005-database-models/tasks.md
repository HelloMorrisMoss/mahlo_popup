**Propagated**: 2026-08-20 — Added tasks for usage-tracking log models.

# Tasks: Database Models & ORM

**Input**: Design documents from `/specs/005-database-models/`

## Phase 1: Setup
- [x] T001 Initialize SQLAlchemy instance (`sqla_instance.py`)
- [x] T002 Create `ModelWrapper` with shared persistence logic

## Phase 2: Foundational
- [x] T003 [P] Configure Flask-SQLAlchemy in the main app
- [x] T004 Implement thread-safe session cleanup handlers

## Phase 3: User Story 1 - Defect Persistence 🎯 MVP
- [x] T005 [P] [US1] Define `DefectModel` with all production columns
- [x] T006 [US1] Implement automatic timestamping logic
- [x] T007 [US1] Create `find_new` query for unconfirmed defects

## Phase 4: User Story 2 - Operator Management
- [x] T008 [P] [US2] Define `OperatorModel` for staff management
- [x] T009 [US2] Implement CRUD helpers for operators

## Phase 5: User Stories 3 & 4 - Usage Tracking
- [ ] T014 [P] [US3] Define `DefectQueryLogModel` with defect_id, timestamp, and source fields
- [ ] T015 [P] [US4] Define `DefectInsertionLogModel` with defect_id, timestamp, and report_name fields
- [ ] T016 [US3/4] Establish foreign key relationships in `DefectModel`

## Phase N: Polish & Gaps
- [x] T010 Create integration tests for `DefectModel`
- [ ] T011 Implement database migrations using Alembic
- [ ] T012 Refactor `ModelWrapper` for SQLAlchemy 2.0
- [ ] T013 Add unit tests for `OperatorModel`
