# Feature Specification: Database Models & ORM

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Refined
**Refined**: 2026-08-20 — Added requirements for tracking defect record queries and report insertions via linked log models.

**Input**: User description: "Data structure and persistence layer for the Mahlo Popup application using SQLAlchemy ORM."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Defect Persistence (Priority: P1)

As a system, I want to save defect records with all relevant production metadata so that they can be analyzed later.
**Why this priority**: Core value proposition of the app.
**Independent Test**: Create a `DefectModel` instance, save it, and verify its presence in the database with `find_by_id`.

**Acceptance Scenarios**:
1. **Given** a new defect is found, **When** the operator confirms it, **Then** all fields (lot, timestamps, affected sections) are saved correctly.

---

### User Story 2 - Operator Management (Priority: P2)

As an administrator, I want to manage a list of authorized operators so that I can track who logged each defect.
**Why this priority**: Accountability and data traceability.
**Independent Test**: Create an operator and verify they can be retrieved by their initials.

---

### User Story 3 - Defect Query Tracking (Priority: P3)

As a system administrator, I want to track which defects are returned in queries and from what source so that I can audit data access.
**Why this priority**: Traceability and usage auditing.
**Independent Test**: Perform a query for defects and verify that `DefectQueryLogModel` entries are created for each.

---

### User Story 4 - Defect Insertion Tracking (Priority: P3)

As a system administrator, I want to record when a defect is successfully inserted into a generated report so that I can track report completion.
**Why this priority**: Verification of data usage in final deliverables.
**Independent Test**: Signal an insertion via the API and verify a `DefectInsertionLogModel` entry is created.

---

### Edge Cases

- Saving a defect with a missing mandatory lot number.
- Handling duplicate operator initials.

## Requirements *(mandatory)*

### Desktop UI Requirements (Tkinter)

- **UI-001**: Display operator names and initials retrieved from the database.

### API Requirements (Flask)

- **API-001**: Use the models to handle all CRUD operations through REST resources.

### Database Migrations (SQLAlchemy)

- **DB-001**: Use SQLAlchemy 2.x declarative base.
- **DB-002**: Support automatic timestamping for record creation.
- **DB-003**: Implement `DefectQueryLogModel` with many-to-one relationship to `DefectModel`, including `timestamp` and `source`.
- **DB-004**: Implement `DefectInsertionLogModel` with many-to-one relationship to `DefectModel`, including `timestamp` and `report_name`.

### Functional Requirements

- **FR-001**: Persist data in PostgreSQL.
- **FR-002**: Ensure thread-safe session management.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All defect fields are persisted correctly including booleans for sections.
- **SC-002**: Timestamps are automatically populated on save.
- **SC-003**: Failed transactions are successfully rolled back.
- **SC-004**: Every query for defects via the `/defects` endpoint generates corresponding query log entries.
- **SC-005**: Defect insertions reported to the system are reliably logged with report name.

## Assumptions

- The database schema is managed via SQLAlchemy `create_all()` or similar (migrations to be added).
- PostgreSQL is the primary production database.
