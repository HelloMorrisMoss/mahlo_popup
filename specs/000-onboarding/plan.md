# Implementation Plan - SDD Onboarding & Bootstrap

## Feature Overview

- **Feature Name**: SDD Onboarding
- **Spec Path**: `specs/000-onboarding/spec.md`
- **Plan Path**: `specs/000-onboarding/plan.md`
- **Tasks Path**: `specs/000-onboarding/tasks.md`

## Technical Context

- **Primary Stack**: Python, Tkinter, Flask
- **Communication**: Thread-safe deques (`f2p_queue`, `p2f_queue`)
- **Configuration**: Spec Kit (.specify)

## Implementation Phases

### Phase 1: Discovery & Architecture

- [x] Run `/speckit.brownfield.scan` to identify project profile.
- [x] Create `ARCHITECTURE.md` documenting the hybrid threading model.

### Phase 2: Bootstrap Configuration

- [x] Create project-aware `constitution.md`.
- [x] Customize templates for specs, plans, and tasks.
- [x] Define agent boundaries in `AGENTS.md`.

## Source Code (mahlo-popup layout)

```text
.specify/
├── memory/
│   └── constitution.md
├── templates/
│   ├── spec-template.md
│   ├── plan-template.md
│   └── tasks-template.md
AGENTS.md
ARCHITECTURE.md
```

**Structure Decision**: Hybrid Desktop/Web structure.
