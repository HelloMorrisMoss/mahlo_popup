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

### 3. Help Window (`help_window/`)

A standalone, dynamically configurable help system designed for industrial touchscreens.

- **Technology**: Tkinter, JSON-based templates.
- **Components**:
  - `HelpApp`: Standalone entry point.
  - `ContentManager`: Handles recursive scanning of JSON templates, metadata extraction, and multi-level caching.
  - `HelpFrame`: Orchestrates the layout, behavior controls (Stay on Top, Focus Loss), and background update loops.
  - `NavFrame`: Scrollable, sectioned navigation sidebar.
  - `ArticleViewer`: Renders mixed text/image content and handles inter-article linking.
- **Functionality**:
  - **Caching**: Metadata is cached for near-instant startup.
  - **Background Synchronization**: Automatically checks for content updates on disk and notifies the user.
  - **Independence**: Can be run independently of the `MainWindow` to minimize impact on core operations.

### 4. Web Server (`flask_server_files/`)

A background service providing RESTful endpoints and web views.

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

### Threading Model

The application uses two primary threads:

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
