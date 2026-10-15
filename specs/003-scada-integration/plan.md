# Implementation Plan: SCADA Integration

**Branch**: `production` | **Date**: 2026-07-10 | **Spec**: [specs/003-scada-integration/spec.md]

## Summary

This feature handles the integration with Ignition SCADA, primarily through database queries to a PostgreSQL/TimescaleDB backend for tag history and REST calls for real-time signaling.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: psycopg2, requests

**Storage**: PostgreSQL (SCADA Tag History)

**Testing**: Manual via Ignition script console, unittest (mocked)

**Target Platform**: Integration with Ignition SCADA

**Project Type**: integration

**Performance Goals**: < 200ms query latency

**Constraints**: Network access to SCADA database

## Constitution Check

- [x] Use of specialized connectors for external databases.
- [x] Machine-specific tag path mapping.
- [x] Error handling for missing historized tags.

## Project Structure

### Documentation (this feature)

```text
specs/003-scada-integration/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (mahlo-popup layout)

```text
scada_outbound_connections/
└── scada_tag_query.py  # TagHistoryConnector
ignition_scada/
├── testing_rest_api.py # SCADA test scripts
└── defect_process.puml # Process diagrams
```

**Structure Decision**: Hybrid Desktop/Web structure.

## Implementation Details

1. **Tag Path Mapping**: The `TagIds` class maps logical fields (e.g., `lot_number`) to specific SCADA tag paths (e.g., `mahlo/lam1/batchid`).
2. **History Connector**: `TagHistoryConnector` manages the connection and executes SQL queries against the `sqlth_1_data` (data) and `sqlth_te` (tag entry) tables.
3. **Data Retrieval**: Methods like `get_recent_lots` and `current_mahlo_length` provide specialized access to process parameters.
4. **REST Integration**: SCADA scripts use `system.net.httpPost` (Ignition built-in) to send signals to the Popup's `/popup` or `/defect` endpoints.
