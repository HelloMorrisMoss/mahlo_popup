# Tasks: SCADA Integration

**Input**: Design documents from `/specs/003-scada-integration/`

## Phase 1: Setup
- [x] T001 Implement base `DatabaseConnection` using `psycopg2`

## Phase 2: Foundational
- [x] T002 Create `TagHistoryConnector` for specialized SCADA queries
- [x] T003 [P] Implement tag ID resolution from paths using `sqlth_te` table

## Phase 3: User Story 1 - Tag History Retrieval 🎯 MVP
- [x] T004 [P] [US1] Implement `get_recent_lots` for operator selection
- [x] T005 [US1] Create machine-specific tag mappings (`lam1`, `lam2`)

## Phase 4: User Story 2 - Real-time Status Monitoring
- [x] T006 [US2] Implement `current_mahlo_length` and other tag queries
- [x] T007 [US2] Add support for shift, recipe, and file name tags

## Phase 5: User Story 3 - SCADA-Triggered Popup
- [x] T008 [US3] Create `testing_rest_api.py` for validating Flask endpoints
- [x] T009 [US3] Implement `defect_tag_change.py` for SCADA side handling

## Phase N: Polish & Gaps
- [ ] T010 Add automated integration tests for `TagHistoryConnector`
- [ ] T011 Implement more robust error handling
- [ ] T012 Externalize tag paths to configuration
