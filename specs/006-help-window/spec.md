# Feature Specification: Dynamically Configurable Help Window

**Feature Branch**: `feature/help-window`

**Created**: 2026-07-17

**Status**: Refined

**Refined**: 2026-07-20 — Added User Story 5 and requirements HLP-007, HLP-013, HLP-014 for video player support and
silent playback in loud industrial environments.

**Input**: User description for a dynamically configurable help window suitable for industrial HMI touchscreens.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Help Navigation (Priority: P1)

As an operator wearing safety gloves, I want to easily navigate through help topics using a side-bar list so that I can
find information without struggling with small UI elements.
**Why this priority**: Core navigation requirement.
**Independent Test**: Verify that the navigation list is populated from template files and clicking an item loads the
corresponding article.

**Acceptance Scenarios**:

1. **Given** multiple help template files in organized folders, **When** the help window is opened, **Then** a
   navigation list is displayed with folder names as section headers and article titles as items.
2. **Given** the navigation list, **When** an item is clicked, **Then** the item is highlighted, and its content is
   displayed in the main frame with the title shown above.

---

### User Story 2 - Window Behavior Controls (Priority: P2)

As an operator, I want to control whether the help window stays open when I click away so that I can follow instructions
while interacting with other applications.
**Why this priority**: Usability in a multi-application environment.
**Independent Test**: Toggle the "Stay Open" setting and verify window behavior when focus is lost.

**Acceptance Scenarios**:

1. **Given** "Stay Open" is enabled, **When** focus is lost, **Then** the window remains visible and stays on top of
   other windows.
2. **Given** "Stay Open" is disabled, **When** focus is lost, **Then** the window closes automatically.

---

### User Story 3 - Content Updates & Caching (Priority: P2)

As a system administrator, I want help content to be cached for performance but also updated automatically in the
background so that operators always have the latest information without performance lag.
**Why this priority**: Performance and maintenance efficiency.
**Independent Test**: Modify a template file and verify that an update indicator appears in the help window.

**Acceptance Scenarios**:

1. **Given** the help window is open, **When** a background check detects changes in the template files, **Then** an "
   Update Available" option is shown.
2. **Given** an update is available, **When** the window is reopened later, **Then** it shows the updated content even
   if the "Update" option wasn't manually clicked previously (due to background caching).

---

### User Story 4 - Error Handling (Priority: P3)

As an operator, I want to know if a help article is broken so that I can contact support instead of being confused by a
blank screen or error message.
**Why this priority**: Robustness and supportability.
**Independent Test**: Create a malformed JSON template and verify it shows as broken in the list.

**Acceptance Scenarios**:

1. **Given** a malformed article template, **When** the help window loads the list, **Then** the item is shown with a
   clear "Broken" indicator.
2. **Given** a broken article is selected, **When** clicked, **Then** a default "Contact Support" article is displayed.

---

### User Story 5 - Rich Content & Linking (Priority: P2)

As an operator, I want to see images, click links, and watch help videos within articles so that I can better understand
complex procedures even in a loud production environment.
**Why this priority**: Effective communication of help content.
**Independent Test**: Click a link in an article and verify it navigates to the linked topic; load an article with a
video block and verify the video player appears.

**Acceptance Scenarios**:

1. **Given** an article with a link to another topic, **When** the link is clicked, **Then** the target topic is loaded
   and highlighted in the navigation list as if it were clicked directly.
2. **Given** an article template containing a "video" block, **When** the article is loaded, **Then** an inline video
   player is displayed within the content flow.
3. **Given** a video player is displayed, **When** the play button is clicked, **Then** the video playback starts.

## Requirements *(mandatory)*

### UI/UX Requirements

- **HLP-001**: Navigation list MUST be touchscreen friendly (large hit targets for safety gloves).
- **HLP-002**: Navigation list MUST be toggleable (show/hide).
- **HLP-003**: Window MUST be resizable.
- **HLP-004**: Window MUST support "Always on Top" when "Stay Open" mode is active.

### Functional Requirements

- **HLP-005**: Help list MUST be generated dynamically from template files (JSON).
- **HLP-006**: Template folders MUST be displayed as section headers in the navigation list.
- **HLP-007**: Content MUST support mixed text, images, internal links, and embedded video players.
- **HLP-008**: System MUST cache the article list and background-check for updates.
- **HLP-009**: System MUST default to 'help for help' article on first load.
- **HLP-013**: Video player MUST support basic playback controls (Play/Pause/Seek) and silent operation by default.
- **HLP-014**: Video player implementation SHOULD be modular to allow switching between different backend
  implementations.

### Technical Requirements

- **HLP-010**: Standalone execution: `help_window` must be runnable independently of `main_window.py`.
- **HLP-011**: Error handling for malformed templates: show title/filename with broken indicator.
- **HLP-012**: Use `ArticleViewer` component (refined from reference) for content display.

## Success Criteria *(mandatory)*

- **SC-001**: Help window loads and displays the navigation list in < 500ms (using cache).
- **SC-002**: Navigation between articles is instantaneous for the operator.
- **SC-003**: "Stay Open" mode correctly keeps the window topmost without focus theft.
- **SC-004**: Background update mechanism does not impact UI responsiveness.

## Assumptions

- Template files are stored in a specific directory (e.g., `help_content/`).
- Images are stored locally or accessible via local path.
- The system runs on Windows (consistent with project environment).
