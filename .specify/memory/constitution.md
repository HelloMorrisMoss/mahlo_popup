# mahlo-popup Constitution

## Core Principles

### I. Hybrid Threaded Architecture

The application MUST maintain responsiveness by separating the UI and Server concerns.

- **Main Thread**: Reserved EXCLUSIVELY for the Tkinter event loop. No blocking I/O or heavy computation.
- **Flask Thread**: Runs the REST API and background schedulers.
- **Communication**: Inter-thread communication MUST use `collections.deque` objects (`f2p_queue`, `p2f_queue`) as
  defined in `main_app.py`.

### II. Pythonic Conventions (PEP 8)

- **Files & Modules**: Use `snake_case` (e.g., `defect_model.py`).
- **Classes**: Use `PascalCase` (e.g., `MainWindow`).
- **Functions & Variables**: Use `snake_case`.
- **Constants**: Use `UPPER_SNAKE_CASE`.

### III. Test-First Migration

Existing code lacks full coverage. New features and refactors MUST include:

- Unit tests in `tests/unit/`.
- Integration tests in `tests/integration/` (especially for SQLAlchemy models).
- Usage of `unittest` and `Flask-Testing`.

### IV. SCADA Integration Safety

Integrations with Ignition SCADA MUST be isolated in `ignition_scada/` and `scada_outbound_connections/`.

- Always handle `requests` exceptions.
- Implement timeouts for all outbound network calls.
- Use centralized logging in `log_and_alert/`.

### V. Single Instance Enforcement

The application MUST ensure only one instance runs per machine using the `mahlo_popup.lock` file mechanism in
`main_app.py`.

### VI. Minimal Disruption

This application SHOULD be an enhancement to the existing HMI, as such:
The application MUST NOT break the functionality of the existing vendor programs on the HMI.
The application SHOULD minimize its impact on the operator's workflow when using the HMI.

## Code Boundaries

- **Entry Point**: `main_app.py`
- **UI Logic**: `main_window.py` and `widgets/`
- **Web API**: `flask_server_files/resources/`
- **Database Models**: `flask_server_files/models/`
- **Configurations**: `untracked_config/` (for environment-specific data)

## Development Workflow

### 1. Specification

Every change starts with a `/speckit.specify` call to generate a `spec.md`. Specs for this project MUST distinguish
between Desktop UI changes and Backend API changes.

### 2. Implementation

- Use `uv` for dependency management.
- Update `pyproject.toml` when adding new dependencies.
- Ensure all tests pass before submission.

## Governance

- This constitution supersedes all other documentation.
- Any deviation from the threading model requires an Architecture Decision Record (ADR).

**Version**: 1.0.0 | **Ratified**: 2026-07-10 | **Last Amended**: 2026-07-10
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
