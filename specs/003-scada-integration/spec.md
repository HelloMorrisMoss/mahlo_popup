# Feature Specification: SCADA Integration

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Migrated

**Input**: User description: "Bidirectional communication between the Mahlo Popup application and the Ignition SCADA system."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tag History Retrieval (Priority: P1)

As an operator, I want to see a list of recent lot numbers from SCADA so that I can quickly select the current production lot.
**Why this priority**: Essential for accurate defect logging and operator efficiency.
**Independent Test**: Call `get_recent_lots()` and verify it returns a list of the 5 most recent lots from the SCADA database.

**Acceptance Scenarios**:
1. **Given** the SCADA database has lot history, **When** the operator opens the selection list, **Then** the 5 most recent lots are displayed.

---

### User Story 2 - Real-time Status Monitoring (Priority: P1)

As a system, I want to retrieve current machine parameters (length, recipe) from SCADA so that defect records are enriched with process data.
**Why this priority**: Data integrity for quality reporting.
**Independent Test**: Query a specific tag (e.g., length) and compare it with the value shown in the Ignition designer.

---

### User Story 3 - SCADA-Triggered Popup (Priority: P2)

As an operator, I want the popup to appear automatically when a SCADA event occurs.
**Why this priority**: Proactive notification of quality issues.
**Independent Test**: Use a test script to POST to `/popup` and verify the UI responds.

---

### Edge Cases

- SCADA database connection timeout.
- Missing tag history for a specific machine.

## Requirements *(mandatory)*

### Desktop UI Requirements (Tkinter)

- **UI-001**: Display SCADA-retrieved data in dropdowns and status labels.

### API Requirements (Flask)

- **API-001**: Expose endpoints for SCADA scripts to trigger actions.

### Database Migrations (SQLAlchemy)

- **DB-001**: Store data retrieved from SCADA in the local PostgreSQL database when logging defects.

### Functional Requirements

- **FR-001**: Support querying Ignition tag history in PostgreSQL/Timescale.
- **FR-002**: Map machine identifiers to SCADA tag paths.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: SCADA database queries return data in < 200ms.
- **SC-002**: UI state changes successfully triggered by REST calls from SCADA.

## Assumptions

- Access to the Ignition SCADA database is available via `psycopg2`.
- Tag paths are consistent across machine instances unless mapped otherwise.
