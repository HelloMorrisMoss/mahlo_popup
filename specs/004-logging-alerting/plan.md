# Implementation Plan: Logging & Alerting System

**Branch**: `production` | **Date**: 2026-07-10 | **Spec**: [specs/004-logging-alerting/spec.md]

## Summary

This feature provides centralized logging with breadcrumbs and automated email alerts for critical events, ensuring observability across the multi-threaded application.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: logging (standard lib), smtplib

**Storage**: Rotating local files (`mahlo_popup.log`)

**Testing**: unittest

**Target Platform**: Cross-platform (Windows/Linux)

**Project Type**: library/infrastructure

**Performance Goals**: Minimal overhead for logging operations

**Constraints**: CSV-compatible log formatting for data analysis

## Constitution Check

- [x] Use of `BreadcrumbFilter` for all log records.
- [x] Global exception hook implementation.
- [x] Rotating file handler to manage disk space.

## Project Structure

### Documentation (this feature)

```text
specs/004-logging-alerting/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (mahlo-popup layout)

```text
log_and_alert/
├── log_setup.py        # Logger config
├── email_alert.py      # SMTP integration
└── program_restart_records.py # Restart tracking
```

**Structure Decision**: Hybrid Desktop/Web structure.

## Implementation Details

1. **Breadcrumb Filter**: A custom `logging.Filter` that adds module, function name, and line number to each log record.
2. **Rotating File Handler**: Configured with a 2MB limit and rotating behavior to prevent log files from growing indefinitely.
3. **Custom Formatter**: A `logging.Formatter` subclass that ensures quotes in log messages are escaped to maintain CSV integrity.
4. **Global Exception Hook**: Overriding `sys.excepthook` to ensure any uncaught exception in the main thread is logged as `CRITICAL`.
5. **SMTP Integration**: A `send_email` function that uses `smtplib.SMTP` to transmit MIME-formatted text emails.
