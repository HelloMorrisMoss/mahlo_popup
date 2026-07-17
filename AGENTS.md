# Agents: mahlo-popup

This project uses a hybrid architecture. Agents are divided by their primary threading and framework context.

## 1. Desktop UI Agent

- **Ownership**: `main_window.py`, `help_window/`, `widgets/`, `Azure-ttk-theme-main/`
- **Context**: Tkinter event loop, main thread responsiveness, Azure theme application.
- **Rules**:
    - MUST NOT perform blocking I/O in the main thread.
    - MUST interact with the Flask server via `outbound_queue` (`p2f_queue`).
    - MUST poll `inbound_queue` (`f2p_queue`) for UI updates.

## 2. Web API Agent

- **Ownership**: `flask_server_files/`, `ignition_scada/`, `scada_outbound_connections/`
- **Context**: Flask REST API, SQLAlchemy ORM, Background scheduling (APScheduler), SCADA integration.
- **Rules**:
    - Responsible for all database interactions.
    - Handles all outbound network requests (SCADA, Email).
    - MUST communicate with the UI via `queues.out_message_queue` (`f2p_queue`).

## 3. Core/Infrastructure Agent

- **Ownership**: `main_app.py`, `log_and_alert/`, `untracked_config/`
- **Context**: Thread orchestration, single-instance locking, logging infrastructure.
- **Rules**:
    - Manages the lifecycle of both the UI and API threads.
    - Ensures fatal errors in one thread are logged and handled (restarts).

## Inter-Agent Communication

All communication between the **Desktop UI Agent** and **Web API Agent** MUST happen via the `deque` queues initialized
in `main_app.py`. Direct function calls or shared variable modification across thread boundaries are STRICTLY FORBIDDEN.
