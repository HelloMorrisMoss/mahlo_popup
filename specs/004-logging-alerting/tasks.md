# Tasks: Logging & Alerting System

**Input**: Design documents from `/specs/004-logging-alerting/`

## Phase 1: Setup
- [x] T001 Implement `BreadcrumbFilter` for enhanced log context
- [x] T002 Configure base logger with `DEBUG`/`INFO` levels

## Phase 2: Foundational
- [x] T003 [P] Set up `RotatingFileHandler` with CSV formatting
- [x] T004 Implement `CustomFormatter` to handle quote escaping

## Phase 3: User Story 1 - Error Logging 🎯 MVP
- [x] T005 [P] [US1] Implement `handle_exception` hook for `sys.excepthook`
- [x] T006 [US1] Ensure traceback info is included in critical logs

## Phase 4: User Story 2 - Automated Alerting
- [x] T007 [P] [US2] Implement core `send_email` using `smtplib`
- [x] T008 [US2] Create `set_up_alert` wrapper for configuration-driven alerts

## Phase 5: User Story 3 - Audit Trail & Breadcrumbs
- [x] T009 [US3] Implement `program_restart_records.py` logic
- [x] T010 [US3] Integrate restart records with main logging flow

## Phase N: Polish & Gaps
- [ ] T011 Relocate log file to project-root relative path
- [ ] T012 Add unit tests for `BreadcrumbFilter` and `CustomFormatter`
- [ ] T013 Implement support for email attachments
- [ ] T014 Add support for multiple log levels in email alerts
