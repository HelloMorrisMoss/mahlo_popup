# Feature Specification: Desktop UI (Tkinter)

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Migrated

**Input**: User description: "The primary desktop interface for the Mahlo Popup application, built using Tkinter."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Defect Logging (Priority: P1)

As an operator, I want to click a defect button so that I can log a quality issue.
**Why this priority**: Core functionality of the application.
**Independent Test**: Verify that clicking a defect button sends a message to the outbound queue and updates the UI status.

**Acceptance Scenarios**:
1. **Given** the application is running, **When** the operator clicks a defect button, **Then** a log entry is created in the database and the UI provides visual feedback.

---

### User Story 2 - Real-time Messaging (Priority: P1)

As an operator, I want to receive real-time alerts from the SCADA system so that I can respond to process changes.
**Why this priority**: Essential for operational awareness.
**Independent Test**: Inject a message into the inbound queue and verify it appears in the UI within 100ms.

**Acceptance Scenarios**:
1. **Given** a new message is received in the inbound queue, **When** the UI polls the queue, **Then** the message is displayed to the operator.

---

### User Story 3 - Window Management (Priority: P2)

As an operator, I want the application to stay on top and remember its position so that it is always accessible and correctly placed.
**Why this priority**: Usability and consistent operator experience.
**Independent Test**: Move the window, restart the app, and verify it returns to the same position.

**Acceptance Scenarios**:
1. **Given** the "Always on Top" setting is enabled, **When** another application is focused, **Then** Mahlo Popup remains visible.
2. **Given** the application window is moved, **When** the application is restarted, **Then** it opens at the last saved coordinates.

---

### User Story 4 - Independent Controls (Priority: P3)

As an operator, I want to use the independent controls panel to manage specific parameters.
**Why this priority**: Provides additional control over the process.
**Independent Test**: Open the independent controls panel and verify interaction with widgets.

---

### User Story 5 - Help and Messaging (Priority: P3)

As an operator, I want to access help and system messages.
**Why this priority**: Supportability and system diagnostics.
**Independent Test**: Open the help window and system message window.

---

### Edge Cases

- What happens when the inbound queue overflows?
- How does the system handle a loss of connection to the Flask backend?

## Requirements *(mandatory)*

### Desktop UI Requirements (Tkinter)

- **UI-001**: Use Azure ttk theme for styling.
- **UI-002**: Implement a polling mechanism using `after()` to check for queue messages.
- **UI-003**: Ensure the UI remains responsive during high message volumes.
- **UI-004**: Handle thread-safe communication using `collections.deque`.

### API Requirements (Flask)

- **API-001**: Interface with the Flask server for defect logging and status updates.

### Database Migrations (SQLAlchemy)

- **DB-001**: Log defect data to the PostgreSQL database via the SQLAlchemy models.

### Functional Requirements

- **FR-001**: System MUST maintain a responsive UI.
- **FR-002**: System MUST support "Always on Top" functionality.
- **FR-003**: System MUST persist window position across restarts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: UI remains responsive (no freezing) during message processing.
- **SC-002**: Window position is correctly restored upon launch.
- **SC-003**: Messages from the inbound queue are processed within < 100ms.

## Assumptions

- The operator has a touch-screen or mouse for interaction.
- The application runs on a Windows-based PC.
