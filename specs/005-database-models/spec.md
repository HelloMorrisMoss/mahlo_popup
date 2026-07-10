# Feature Specification: Database Models & ORM

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Migrated

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

### Functional Requirements

- **FR-001**: Persist data in PostgreSQL.
- **FR-002**: Ensure thread-safe session management.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All defect fields are persisted correctly including booleans for sections.
- **SC-002**: Timestamps are automatically populated on save.
- **SC-003**: Failed transactions are successfully rolled back.

## Assumptions

- The database schema is managed via SQLAlchemy `create_all()` or similar (migrations to be added).
- PostgreSQL is the primary production database.
