# Feature Specification: Dynamically Configurable Help Window

**Feature Branch**: `feature/help-window`

**Created**: 2026-07-17

**Status**: Refined
**Refined**: 2026-07-21 — Added requirement HLP-024 for configurable editor access.
**Refined**: 2026-07-21 — Added requirements for Multi-process integration (Option 2), Flask API, and Main Window
integration.

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
4. **Given** an article with a large image or video, **When** the article is loaded, **Then** the media is automatically
   scaled to fit within the visible width of the article viewer.
5. **Given** a media block with "size" metadata (e.g., "small"), **When** the article is loaded, **Then** the media is
   scaled according to the specified size relative to the viewer width.

---

### User Story 6 - Article Editor (Priority: P3)

As a non-developer content creator, I want a WYSIWYG editor to create and modify help articles so that I don't have to
manually edit JSON files.
**Why this priority**: Ease of maintenance for non-developers.
**Independent Test**: Open the editor, add/edit/reorder blocks, and verify the changes are reflected in the Help Window
and correctly saved to disk.

**Acceptance Scenarios**:

1. **Given** the help window is in "Edit Mode", **When** the editor controls are used, **Then** blocks can be added,
   removed, or reordered within the article.
2. **Given** the editor is active, **When** a change is made (e.g., editing text or changing an image), **Then** the
   changes are immediately propagated to the `ArticleViewer` for live preview.
3. **Given** the file manager in the editor, **When** a folder or file is renamed, **Then** all internal links and
   media references within other articles are updated to reflect the new paths.
4. **Given** a new article is created, **When** saved, **Then** it appears correctly in the navigation list and is
   persisted as a JSON file in the appropriate directory.
5. **Given** the help window is initialized without "Edit Mode" enabled, **When** the window is displayed, **Then**
   the "Edit Content" button is not visible.

---

### User Story 7 - Help Content Management (Priority: P3)

As a content maintainer, I want to be able to move articles between folders and consolidate media files so that I can
keep the help system organized as it grows.
**Why this priority**: Long-term maintainability.
**Independent Test**: Move an article to a different folder and verify all links to it still work; use "Consolidate
Media" to move an article's media into its category-specific media folder.

**Acceptance Scenarios**:

1. **Given** the editor's file manager, **When** a "Move to Folder" action is performed on an article, **Then** the file
   is moved on disk and all internal links in other articles are automatically updated.
2. **Given** an article with media stored in external or "wrong" folders, **When** the "Consolidate Media" action is
   triggered, **Then** the referenced media files are copied to the article's category media folder and the article's
   JSON is updated with the new paths.

---

### User Story 8 - Main Window Integration (Priority: P2)

As an operator, I want to open the help window directly from the main popup control panel so that I can quickly access
instructions without leaving the application context.
**Why this priority**: Essential for making the help system accessible during production.
**Independent Test**: Click the "Help" button in the MainWindow and verify the Help Window launches as a separate
process.

**Acceptance Scenarios**:

1. **Given** the Main Popup is open, **When** the "Help" button on the control panel is clicked, **Then** the Help
   Window starts in its own process.
2. **Given** the Help Window is already open, **When** the "Help" button is clicked again, **Then** the existing
   Help Window is brought to the front and focused, instead of opening a second instance.
3. **Given** the Help Window has a fatal error or is closed, **When** the Main Popup remains open, **Then** the
   Main Popup continues to function normally without interruption.

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
- **HLP-015**: Responsive Media Scaling: Images and videos MUST be automatically scaled to fit within the article
  viewer's visible width. This constraint is mandatory and supersedes any configured dimensions or presets (per HLP-016)
  that would result in content overflowing the viewer area.
- **HLP-016**: Media Metadata Support: The article JSON structure MUST support optional metadata for media blocks to
  define display sizes. Supported formats include named presets (`thumbnail`, `small`, `medium`, `large`, `fill`),
  absolute pixel dimensions (e.g., "1441x1080"), and percentages of the available viewer width.
- **HLP-017**: WYSIWYG Editor Module: The editor MUST be implemented in a separate module/package to maintain separation
  of concerns from the core viewer.
- **HLP-018**: Block Management: The editor MUST support adding, removing, and reordering blocks (headers, paragraphs,
  images, videos, links).
- **HLP-019**: Content Persistence: The editor MUST correctly serialize and deserialize the help system's JSON format.
- **HLP-020**: Path Integrity: The system MUST automatically update references (internal links, media paths) when files
  or folders are renamed or moved within the help content directory.
- **HLP-021**: Live Preview: The editor SHOULD provide a way to see changes in the `ArticleViewer` context before
  finalizing/saving.
- **HLP-022**: Article Relocation: The editor MUST support moving articles between folders with automatic reference
  updates.
- **HLP-023**: Media Consolidation: The editor MUST provide a mechanism to "pull" or consolidate media referenced in an
  article into its designated category-specific media folder.
- **HLP-024**: Configurable Editor Access: The "Edit Content" button MUST be optional and disabled by default to prevent
  unauthorized or accidental modifications by operators on production HMIs.
- **HLP-025**: Multi-process Integration: The Help Window MUST be launched as a separate operating system process
  from the Main Window to ensure process isolation and stability.
- **HLP-026**: Single Instance with "Bring-to-Front": The Help System MUST enforce a single instance across the OS.
  Subsequent launch attempts MUST signal the existing instance to `lift()` and `focus()` itself.
- **HLP-027**: Minimal Web API (Flask): The Help Window MUST include a minimal Flask-based web server to support
  cross-process signaling and future web-based help features.
- **HLP-028**: Main Window UI Integration: A "Help" button MUST be added to the `MainWindow` control panel,
  positioned after the operator grid button.

### Technical Requirements

- **HLP-010**: Standalone execution: `help_window` must be runnable independently of `main_window.py`.
- **HLP-011**: Error handling for malformed templates: show title/filename with broken indicator.
- **HLP-012**: Use `ArticleViewer` component (refined from reference) for content display.

## Success Criteria *(mandatory)*

- **SC-001**: Help window loads and displays the navigation list in < 500ms (using cache).
- **SC-002**: Navigation between articles is instantaneous for the operator.
- **SC-003**: "Stay Open" mode correctly keeps the window topmost without focus theft.
- **SC-004**: Background update mechanism does not impact UI responsiveness.
- **SC-005**: Process Isolation: A crash or freeze in the Help Window process MUST NOT affect the Main Window process.
- **SC-006**: Single Instance: Only one Help Window process exists at any given time.

## Assumptions

- Template files are stored in a specific directory (e.g., `help_content/`).
- Images are stored locally or accessible via local path.
- The system runs on Windows (consistent with project environment).
