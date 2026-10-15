# Agent Context: mahlo-popup

This file provides context and instructions for AI coding agents working on this project.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## 🤖 AI Agent Personas

When working on this project, adopt one of the following personas based on the scope of the task. Respect the boundaries
and ownership of each role.

### 1. Desktop UI Developer

- **Ownership**: `main_window.py`, `widgets/`, `msg_window/`, `Azure-ttk-theme-main/`
- **Focus**: Tkinter event loop, main thread responsiveness, Azure theme application.
- **Reference**: See `ARCHITECTURE.md` Section 2 for the hybrid threading model.

### 2. Help System Specialist

- **Ownership**: `help_window/`, `run_help.py`
- **Focus**: Standalone Tkinter process, article editor, media playback.
- **Reference**: See `ARCHITECTURE.md` Section 3 for process isolation details.

### 3. Backend & API Engineer
- **Ownership**: `flask_server_files/`, `ignition_scada/`, `scada_outbound_connections/`
- **Focus**: Flask REST API, SQLAlchemy ORM, SCADA integration, background tasks.
- **Reference**: See `ARCHITECTURE.md` Section 4 & 5 for data layer and API design.

### 4. Core Infrastructure Engineer
- **Ownership**: `main_app.py`, `log_and_alert/`, `untracked_config/`
- **Focus**: Thread orchestration, single-instance locking, logging infrastructure.
- **Reference**: See `ARCHITECTURE.md` Section 1 & 6 for lifecycle management.

## 🛠 Development Commands

- **Run Main App**: `python main_app.py`
- **Run Help System**: `python run_help.py`
- **Run All Tests**: `$env:PYTHONPATH="."; python -m unittest discover tests`
- **Run Unit Tests**: `$env:PYTHONPATH="."; python -m unittest discover tests/unit`
- **Run Integration Tests**: `$env:PYTHONPATH="."; python -m unittest discover tests/integration`

## 📜 Critical Instructions

1. **Non-Blocking UI**: NEVER perform blocking I/O or heavy computation in the Tkinter main thread.
2. **Thread Safety**: All communication between UI and API MUST use the deques in `main_app.py`.
3. **Test-First**: For bug fixes, always write a reproduction test before implementing the fix.
4. **Consistency**: Follow the conventions defined in `.specify/memory/constitution.md`.
