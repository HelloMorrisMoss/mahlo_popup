# Implementation Plan: Desktop UI (Tkinter)

**Branch**: `production` | **Date**: 2026-07-10 | **Spec**: [specs/001-desktop-ui/spec.md]

## Summary

The Desktop UI is the primary interface for operators, built with Tkinter and the Azure ttk theme. It communicates with the Flask backend and SCADA systems via thread-safe queues.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Tkinter, Azure ttk theme, collections.deque

**Storage**: Local window configuration (position, always-on-top)

**Testing**: unittest

**Target Platform**: Windows Desktop

**Project Type**: desktop-app

**Performance Goals**: < 100ms message processing latency

**Constraints**: Must remain responsive under high SCADA message load

## Constitution Check

- [x] Pythonic snake_case for files and methods.
- [x] Thread-safe queue usage for UI updates.
- [x] Azure theme styling consistent with guidelines.

## Project Structure

### Documentation (this feature)

```text
specs/001-desktop-ui/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (mahlo-popup layout)

```text
widgets/                # Custom Tkinter components
main_window.py          # Main Tkinter UI
help_window.py          # Help interface
msg_window/             # Messaging interface
```

**Structure Decision**: Hybrid Desktop/Web structure.

## Implementation Details

1. **Main Loop**: Standard Tkinter `mainloop()` running in the main thread.
2. **Queue Monitoring**: Periodic polling (via `after()`) of the inbound queue to process messages from background threads.
3. **Event Handling**: Binding physical and virtual events to UI actions.
4. **State Management**: Local tracking of operator selections and system status to drive UI updates.
5. **Batch Clearing**: `Clear Old Records` iterates through active message panels, sets their state to "nothing
   removed", marks records for deletion, and saves them.
6. **Confirmation Logic**: Multi-click countdown for system restart implemented with `after()` for timeout resets.
7. **Grid Selection**: `OperatorGridWindow` dynamically builds a grid of buttons from the operator list, including
   alphabetical disabled headers for navigation.
