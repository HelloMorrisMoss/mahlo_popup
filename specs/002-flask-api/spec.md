# Feature Specification: Flask REST API

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Refined
**Refined**: 2026-07-15 — Added host system monitoring features including PrintSVR.exe watchdog and PDF report discovery
endpoint.
**Refined**: 2026-07-15 — Updated PrintSVR.exe watchdog requirements to ensure independent process detachment and
correct working directory.

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

### User Story 4 - Host System Watchdog (Priority: P3)

As a systems administrator, I want to ensure the `PrintSVR.exe` process is always running so that PDF reports are
generated without interruption.
**Why this priority**: Operational reliability of report generation.
**Independent Test**: Terminate `PrintSVR.exe` and verify it is restarted by the watchdog. Verify notification on
failure.

**Acceptance Scenarios**:

1. **Given** `PrintSVR.exe` is not running, **When** the watchdog check occurs, **Then** the system attempts to restart
   it from the configured path as an independent (detached) process, starting in the executable's directory.
2. **Given** a restart attempt fails, **When** the failure is detected, **Then** a POST request is sent to `/button_msg`
   with a specific error message.

---

### User Story 5 - PDF Report Monitoring (Priority: P3)

As a systems integrator, I want other systems to be able to check for recently created PDF reports via a REST endpoint.
**Why this priority**: Integration with external monitoring and verification of report generation.
**Independent Test**: Call `GET /host_monitor` after creating a dummy PDF in the target directory and verify it is
detected.

**Acceptance Scenarios**:

1. **Given** a new PDF file exists in the search window, **When** `GET /host_monitor` is called, **Then** it returns
   `new_report_found: true` and the file path.
2. **Given** no new PDF file exists, **When** `GET /host_monitor` is called, **Then** it returns
   `new_report_found: false`.

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
- **API-004**: Implement `/host_monitor` endpoint with PDF creation check logic.

### Database Migrations (SQLAlchemy)

- **DB-001**: Integrate with SQLAlchemy for PostgreSQL persistence.

### Functional Requirements

- **FR-001**: System MUST provide a stable RESTful interface.
- **FR-002**: System MUST support background processing via APScheduler.
- **FR-003**: System MUST periodically check if `PrintSVR.exe` is running every `printsvr_check_interval_seconds`.
- **FR-004**: System MUST monitor `pdf_root_directory` and the two most recent 'YYYYMMDD' subdirectories for PDF files
  created within `pdf_created_window_seconds`.
- **FR-005**: Watchdog failure MUST trigger a notification via POST to `/button_msg` with the specified error message
  and "PDF Error!" short text.
- **FR-006**: `PrintSVR.exe` MUST be started as an independent process, detached from the `mahlo_popup` process
  hierarchy, ensuring it persists if the popup is closed.
- **FR-007**: `PrintSVR.exe` MUST be started with its parent directory as the current working directory.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All endpoints respond with correct HTTP status codes.
- **SC-002**: Background scheduler processes inbound queue every 10 seconds.
- **SC-003**: Multi-instance conflicts are detected and resolved.
- **SC-004**: `PrintSVR.exe` is automatically restarted if it stops, or a failure is reported.
- **SC-005**: `/host_monitor` correctly reports the presence of new PDF files within the configured window.

## Assumptions

- Flask runs on a dedicated thread in the application.
- API secret key is used for session management (currently placeholder).
