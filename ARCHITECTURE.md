# Architecture: mahlo-popup

This document describes the high-level architecture of the `mahlo-popup` project.

## Overview

The `mahlo-popup` is a hybrid application that combines a **Tkinter-based Desktop Interface** with a **Flask-based Web
Server**. It is designed for defect tracking and operator notifications, integrating with external SCADA systems (
specifically Ignition).

## High-Level Components

### 1. Entry Point (`main_app.py`)

The application entry point is responsible for:

- Ensuring a single instance is running via file locking (`mahlo_popup.lock`).
- Initializing inter-thread communication queues (`f2p_queue`, `p2f_queue`).
- Spawning the Flask web server in a background thread.
- Launching the Tkinter `MainWindow` in the main thread.
- Handling fatal exceptions and program restarts.

### 2. Desktop Interface (`main_window.py` & `widgets/`)

The primary user interface for operators on the plant floor.

- **Technology**: Tkinter with the Azure ttk theme.
- **Main Thread**: Runs the Tkinter event loop.
- **Communication**: Polls `f2p_queue` (Flask-to-Popup) for real-time updates (e.g., new defect signals from SCADA).

### 3. Help System (`help_window/`)

A standalone, dynamically configurable help system that runs as a separate OS process for isolation and stability.

- **Technology**: Tkinter, Flask, JSON templates.
- **Process Model**: Launched as a separate process via `run_help.py`.
- **Components**:
  - `HelpApp`: Process entry point and Tkinter application.
  - `flask_server_files/`: Flask server for inter-process signaling (Bring-to-Front).
    - *Note*: The web-based article editor previously located here is **DEPRECATED** and has been migrated to the
      `mahlo_defect_lookup_table` Management Hub.
  - `editor/`: **DEPRECATED**. WYSIWYG article editor and file management utilities. Content management is now handled
    via the Management Hub.
  - `ContentManager`: handles recursive scanning of JSON templates and multi-level caching.
  - `HelpFrame`: Main UI container with background synchronization loops.
- **Independence**: Isolation ensures that help system operations (like media playback or editing) do not impact the
  core defect tracking responsiveness or stability.

### 4. Main Web Server (`flask_server_files/`)

The primary background service for the defect removal system, providing RESTful endpoints and web views.

- **Technology**: Flask, Waitress (WSGI), APScheduler.
- **REST API**: Located in `flask_server_files/resources/`, handling defects, operators, and signals.
- **Background Tasks**: `APScheduler` monitors communication queues and ensures the program maintains control of its
  assigned network port.

### 5. Data Layer (`flask_server_files/models/`)

- **Technology**: SQLAlchemy ORM with a PostgreSQL backend.
- **Models**: Defines the schema for `DefectModel`, `OperatorModel`, etc.

### 6. Integrations

- **SCADA (`ignition_scada/`)**: Logic for interacting with Ignition SCADA tags and events.
- **Outbound Connections (`scada_outbound_connections/`)**: Handles messaging back to SCADA systems.
- **Alerting (`log_and_alert/`)**: Centralized logging and email notification system.

## Data Flow & Concurrency

### Multi-Process Model

The application leverages OS-level process isolation for the Help System to ensure that resource-intensive tasks (media,
editing) do not interfere with the defect removal mission-critical path.

### Threading Model (Main Process)

The main application process uses two primary threads:

1. **Main Thread**: Dedicated to the Tkinter UI to maintain responsiveness.
2. **Flask Thread**: Runs the Waitress server and background schedulers.

### Inter-Thread Communication

Communication between the threads is handled via `collections.deque` objects:

- **`f2p_queue`**: Flask pushes messages (like SCADA events) here for the Popup to display.
- **`p2f_queue`**: The Popup pushes operator actions or status updates here for the Flask server to process.

## Tech Stack

- **Language**: Python 3.9+
- **UI**: Tkinter, ttkwidgets
- **Web**: Flask, Flask-RESTful, Waitress
- **Database**: PostgreSQL, SQLAlchemy
- **Data Analysis**: Pandas, NumPy
- **Task Scheduling**: APScheduler
