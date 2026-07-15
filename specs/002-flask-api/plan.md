# Implementation Plan: Flask REST API

**Propagated**: 2026-07-15 — Updated from spec.md refinement (Host System Watchdog and PDF Report Monitoring Service)

**Branch**: `production` | **Date**: 2026-07-10 | **Spec**: [specs/002-flask-api/spec.md]

## Summary

The Flask REST API provides the backend services for the application, using Flask-Restful and Waitress. It manages data persistence and handles background tasks via APScheduler.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Flask 2.3.2, Flask-Restful, Waitress, APScheduler

**Storage**: SQLAlchemy (PostgreSQL)

**Testing**: unittest, Flask-Testing

**Target Platform**: Linux/Windows Server

**Project Type**: web-service

**Performance Goals**: Responsive REST endpoints

**Constraints**: Port control logic for unique instances

## Constitution Check

- [x] Use of Flask application factory pattern.
- [x] Background tasks managed via APScheduler.
- [x] Shared SQLAlchemy instance for all resources.

## Project Structure

### Documentation (this feature)

```text
specs/002-flask-api/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (mahlo-popup layout)

```text
flask_server_files/
├── flask_app.py        # App factory
├── resources/          # REST resources
├── models/             # SQLAlchemy models
├── routing.py          # Blueprints
└── sqla_instance.py    # SQLA instance
```

**Structure Decision**: Hybrid Desktop/Web structure.

## Implementation Details

1. **App Initialization**: Flask app is configured with SQLALCHEMY_DATABASE_URI and other settings.
2. **Resource Registration**: Resources are added to the `Api` instance with specific URL patterns.
3. **Threading & Queues**: The `start_flask_app` function takes inbound/outbound queues and shares them with the app context.
4. **Background Watcher**: `schedule_queue_watcher` starts a background thread to poll the inbound queue and check port control.
5. **Waitress Integration**: Production-ready server serving the Flask app on a configured host and port.
6. **Host System Watchdog**: Integrated into APScheduler, this logic monitors the `PrintSVR.exe` process and attempts
   automatic recovery if it is found to be not running. Recovery attempts MUST start the process as an independent,
   detached entity, with the correct working directory as the binary parent directory, to ensure it persists after the
   popup closes.
7. **PDF Report Monitoring Service**: Provides a mechanism to scan the local filesystem for recently generated PDF
   reports based on date-named directory patterns and creation time windows.
