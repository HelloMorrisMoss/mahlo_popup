# Feature Specification: Desktop UI (Tkinter)

**Feature Branch**: `production`

**Created**: 2026-07-10

**Status**: Completed (Migrated)

**Refined**: 2026-07-21 — Added integration for the independent Help Window (HLP-028) in User Story 5 and Requirement
UI-007.
**Refined**: 2026-07-16 — Refined "Always on Top" functionality to prevent Windows taskbar from flashing/activating.
**Implemented**: 2026-07-16 — Applied win32gui fix with `SWP_NOACTIVATE` and `wm_frame()`.

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

1. **Given** the "Always on Top" setting is enabled, **When** another application is focused, **Then** Mahlo Popup
   remains visible and the Windows taskbar does not activate or flash.
2. **Given** the application window is moved, **When** the application is restarted, **Then** it opens at the last saved coordinates.

---

### User Story 4 - Independent Controls (Priority: P3)

As an operator, I want to use the independent controls panel to manage specific parameters.
**Why this priority**: Provides additional control over the process.
**Independent Test**: Open the independent controls panel and verify interaction with widgets.

---

### User Story 5 - Help and System Messages (Priority: P3)

As an operator, I want to access help and see important system messages so that I can understand procedures and stay
informed about system status.
**Why this priority**: Supportability and system diagnostics.
**Independent Test**: Click the "Help" button to launch the independent help process; verify that system messages
correctly display on the main window label via `set_additional_msg`.

**Acceptance Scenarios**:

1. **Given** the Main Window is open, **When** the "Help" button is clicked, **Then** the separate help process is
   launched (as defined in `specs/006-help-window`).
2. **Given** a system notification is triggered, **When** a `set_additional_msg` message is received, **Then** the
   message is displayed on the main window's message label.

---

### User Story 6 - Batch Clearing Defect Records (Priority: P2)

As an operator, I want to clear all open defect records at once when they are no longer relevant.
**Why this priority**: Efficiency for the operator when many stale records accumulate.
**Independent Test**: Click "Clear Old Records" and verify all panels are closed and records are marked for deletion in
the database.

**Acceptance Scenarios**:

1. **Given** an operator is selected, **When** "Clear Old Records" is clicked, **Then** all open defect records are
   saved with "nothing removed" status, `marked_for_deletion` is set to True, and the panels are closed.
2. **Given** no operator is selected, **When** "Clear Old Records" is clicked, **Then** a warning is displayed and no
   records are cleared.

---

### User Story 7 - HMI System Restart (Priority: P2)

As an operator, I want a way to restart the HMI computer from the application when troubleshooting.
**Why this priority**: Troubleshooting support for the plant floor.
**Independent Test**: Verify the countdown mechanism and that an email is logged/sent before the restart command (
mocked).

**Acceptance Scenarios**:

1. **Given** the "Restart Mahlo HMI (3)" button, **When** clicked, **Then** the countdown decreases.
2. **Given** the countdown is at 0, **When** clicked, **Then** an email notification containing contextual information (
   laminator number, hostname, etc.) and the operator's name is sent, and the system restart is initiated.
3. **Given** the button was clicked but not again for 10 seconds, **When** timer expires, **Then** the countdown resets
   to 3.

---

### User Story 8 - Enhanced Operator Selection (Priority: P2)

As an operator, I want an easier way to find and select my name from a large list.
**Why this priority**: Improved usability on touchscreens.
**Independent Test**: Open the operator grid window and select a name.

**Acceptance Scenarios**:

1. **Given** the operator grid window is open, **When** an operator button is clicked, **Then** that operator is
   selected in the main dropdown and the grid window closes.
2. **Given** the operator grid window is open, **Then** operators are displayed in a flex-fill grid with alphabetical
   headers.

---

### Edge Cases

- What happens when the inbound queue overflows?
- How does the system handle a loss of connection to the Flask backend?
- Multiple simultaneous "Clear Old Records" attempts.

## Requirements *(mandatory)*

### Desktop UI Requirements (Tkinter)

- **UI-001**: Use Azure ttk theme for styling.
- **UI-002**: Implement a polling mechanism using `after()` to check for queue messages.
- **UI-003**: Ensure the UI remains responsive during high message volumes.
- **UI-004**: Handle thread-safe communication using `collections.deque`.
- **UI-005**: `IndependentControlsPanel` MUST include "Clear Old Records", "Restart Popup", and "Restart Mahlo HMI"
  buttons.
- **UI-006**: Operator selection MUST provide both a dropdown and a grid-based selection window.
- **UI-007**: MainWindow MUST include a "Help" button in the `IndependentControlsPanel` (positioned after the operator
  grid button) to launch the separate help process.

### API Requirements (Flask)

- **API-001**: Interface with the Flask server for defect logging and status updates.

### Database Migrations (SQLAlchemy)

- **DB-001**: Log defect data to the PostgreSQL database via the SQLAlchemy models.
- **DB-002**: Support `marked_for_deletion` attribute on defect records.

### Functional Requirements

- **FR-001**: System MUST maintain a responsive UI.
- **FR-002**: System MUST support "Always on Top" functionality without activating the Windows taskbar or stealing focus
  during periodic checks.
- **FR-003**: System MUST persist window position across restarts.
- **FR-004**: System restart MUST be protected by a multi-click confirmation and send email notification including
  contextual information.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: UI remains responsive (no freezing) during message processing.
- **SC-002**: Window position is correctly restored upon launch.
- **SC-003**: Messages from the inbound queue are processed within < 100ms.
- **SC-004**: "Clear Old Records" processes all records in < 2 seconds.
- **SC-005**: Operator grid displays all active operators alphabetically.

## Assumptions

- The operator has a touch-screen or mouse for interaction.
- The application runs on a Windows-based PC.
