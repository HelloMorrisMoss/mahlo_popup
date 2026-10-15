**Propagated**: 2026-08-20 — Updated plan to include DefectQueryLogModel and DefectInsertionLogModel for tracking usage.

# Implementation Plan: Database Models & ORM

**Branch**: `production` | **Date**: 2026-07-10 | **Spec**: [specs/005-database-models/spec.md]

## Summary

This feature defines the SQLAlchemy ORM models for the application, specifically `DefectModel`, `OperatorModel`, and tracking models `DefectQueryLogModel` and `DefectInsertionLogModel`.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: SQLAlchemy, Flask-SQLAlchemy

**Storage**: PostgreSQL

**Testing**: unittest (integration tests)

**Target Platform**: Database Server

**Project Type**: library/data-layer

**Performance Goals**: Efficient queries for real-time logging

**Constraints**: Thread-safe sessions for hybrid environment

## Constitution Check

- [x] Use of declarative base for all models.
- [x] Automatic timestamping for creation/updates.
- [x] Scoped sessions for thread safety.

## Project Structure

### Documentation (this feature)

```text
specs/005-database-models/
├── spec.md              # Feature Specification
├── plan.md              # This file
└── tasks.md             # Task list
```

### Source Code (mahlo-popup layout)

```text
flask_server_files/models/
├── defect.py           # DefectModel
├── lam_operator.py     # OperatorModel
├── model_wrapper.py    # Persistence helper
└── sqla_instance.py    # SQLA setup
```

**Structure Decision**: Hybrid Desktop/Web structure.

## Implementation Details

1. **Base Configuration**: Use `sqlalchemy.ext.declarative.declarative_base()` (or Flask-SQLAlchemy's `db.Model`) as the parent for all models.
2. **Dynamic Initialization**: Models support `**kwargs` in `__init__` to dynamically map dictionary data to columns.
3. **Query Helpers**: Class methods like `find_by_id`, `find_new`, and `find_all` abstract the SQLAlchemy session queries.
4. **Timestamping**: Utilize `func.current_timestamp()` and `onupdate` parameters for automatic timestamp management.
5. **Session Scoping**: Implement `teardown_appcontext` in Flask to ensure sessions are removed after each request.
6. **Query Tracking**: `DefectQueryLogModel` will include `defect_id` (FK to `DefectModel.id`), `timestamp`, and `source`. A relationship will be added to `DefectModel` for easy access to its query history.
7. **Insertion Tracking**: `DefectInsertionLogModel` will include `defect_id` (FK to `DefectModel.id`), `timestamp`, and `report_name`.

## Migration Strategy

To ensure zero data loss in the existing `laminator_foam_defect_removal_records` table:

1. **Standalone Script**: Use a migration script that leverages SQLAlchemy's `create_all()` method.
2. **Safety Mechanism**: `create_all()` uses `checkfirst=True` by default, which creates tables only if they do not exist.
3. **ORM Relationships**: Relationships defined in Python code do not affect the physical database schema of existing tables; they only define how SQLAlchemy navigates the data.
4. **Foreign Keys**: These are defined in the new tables, pointing to the existing table's ID, which is a non-destructive operation.
5. **Verification**: The migration script will query the existing table before and after the operation to confirm data integrity.

## Production Migration Procedure

To apply these changes to the production server:

1. **Backup**: Perform a full backup of the production database.
2. **Environment**: Ensure the production environment has updated dependencies (`flask-sqlalchemy`, `psycopg2-binary`).
3. **Execution**: Run the `scripts/db_migration_defect_logs.py` script.
   - This script is designed to be idempotent and safe; it only creates the two new tracking tables.
   - It will NOT alter or delete any data in `laminator_foam_defect_removal_records`.
4. **Verification**: Confirm the script reports "SUCCESS" for both table creation and data integrity verification.
5. **Deployment**: Deploy the updated `mahlo_popup` code to the production server.
