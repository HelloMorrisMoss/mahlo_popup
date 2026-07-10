# Feature Specification: Flask REST API

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Migrated

**Input**: User description: "The backend service for the Mahlo Popup application, implemented using Flask and Flask-Restful."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Defect Management (Priority: P1)

As a system, I want to manage defect records through a REST API so that data can be persisted and retrieved reliably.
**Why this priority**: Core data management function.
**Independent Test**: Use `curl` or `requests` to POST a defect to `/defect` and verify it is saved in the database.

**Acceptance Scenarios**:
1. **Given** a valid defect payload, **When** a POST request is sent to `/defect`, **Then** the record is created and a 201 status is returned.

---

### User Story 2 - UI Signaling via Popups (Priority: P1)

As an operator, I want the system to trigger popups based on SCADA events so that I am notified of critical process states.
**Why this priority**: Main purpose of the application (Mahlo Popup).
**Independent Test**: Send a request to `/popup` and verify the UI displays the corresponding message.

**Acceptance Scenarios**:
1. **Given** a SCADA event requires a popup, **When** the backend receives the signal, **Then** it updates the `/popup` state and signals the UI.

---

### User Story 3 - Background Task Management (Priority: P2)

As a developer, I want background tasks to process queues and monitor system health so that the application remains stable.
**Why this priority**: Operational stability and integration.
**Independent Test**: Verify that APScheduler jobs are running and processing the `p2f_queue`.

---

### Edge Cases

- Port conflict when starting multiple instances.
- Handling database connection loss.

## Requirements *(mandatory)*

### Desktop UI Requirements (Tkinter)

- **UI-001**: UI MUST communicate with Flask via `f2p_queue` and `p2f_queue`.

### API Requirements (Flask)

- **API-001**: Implement REST endpoints using Flask-Restful: `/defect`, `/popup`, `/operator`, `/database`.
- **API-002**: Use Waitress as the WSGI server.
- **API-003**: Implement `check_that_port_is_mine` logic for instance locking.

### Database Migrations (SQLAlchemy)

- **DB-001**: Integrate with SQLAlchemy for PostgreSQL persistence.

### Functional Requirements

- **FR-001**: System MUST provide a stable RESTful interface.
- **FR-002**: System MUST support background processing via APScheduler.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All endpoints respond with correct HTTP status codes.
- **SC-002**: Background scheduler processes inbound queue every 10 seconds.
- **SC-003**: Multi-instance conflicts are detected and resolved.

## Assumptions

- Flask runs on a dedicated thread in the application.
- API secret key is used for session management (currently placeholder).
