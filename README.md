# mahlo_popup

This project needed to be able to do several things: show a popup on an existing HMI screen when operation was stopped, not obstruct the original HMI while in operation, and capture operator feedback about operating conditions - saving it to a database.

It uses a flask RESTful API for the RPC for signaling that operation has stopped/started (built for Ignition SCADA, but it would work with anything that can do HTTP requests), flask SQLalchemy to interact with the database, and a themed tkinter interface for the popup.

It uses a pair of deques for bidrectional communication between the flask server and the tkinter thread. The flask SQLalchemy model has been integrated into the tkinter popup.

## API Documentation

### RESTful API Endpoints

The following endpoints are available under the RESTful API:

#### `/defect`

- **Methods**: `GET`, `POST`, `PUT`
- **Description**: Manage individual defect records.
    - `GET`: Retrieve a defect by `id`. (Requires `?id=###`)
    - `POST`: Create a new defect.
    - `PUT`: Update an existing defect by `id` or create a new one.

#### `/defects`

- **Methods**: `GET`, `PUT`
- **Description**: Manage lists of defects.
    - `GET`: Retrieve a list of defects. Optional filters: `start_date`, `end_date`, `lam_num`.
    - `PUT`: Mark all defects as confirmed by passing `confirm_all=True`.

#### `/popup`

- **Methods**: `POST`
- **Description**: Send commands to the popup window.
- **Parameters**: `action` (required), `new_lot_number` (optional).
- **Supported Actions**: `shrink`, `show`, `show_force`, `defects_updated`, `reset_position`, `restart_popup`,
  `shift_change`, `test_flask_error`, `update_lot_number`.

#### `/operator`

- **Methods**: `GET`, `POST`, `PUT`
- **Description**: Manage individual operator records.
    - `GET`: Retrieve active operators. Optional filter: `lam_number`.
    - `POST`: Create a new operator.
    - `PUT`: Update an existing operator by `id`.

#### `/operators`

- **Methods**: `GET`, `POST`, `PUT`
- **Description**: Manage multiple operator records.
    - `POST`: Create multiple operators from a list of records in the `records` field.

#### `/button_msg`

- **Methods**: `POST`, `PUT`
- **Description**: Send messages to be displayed on the popup window buttons.
- **Parameters**: `additional_message_text`, `additional_message_short_text`, `additional_message_clear`,
  `color_theme` (`info`, `note`, `warning`, `critical`), `additional_message_size` (`small`, `medium`, `large`).

#### `/database`

- **Methods**: `POST`
- **Description**: Database management tasks (Development only).
- **Supported Actions**: `reset_database`.

### Web Interface Routes

These routes provide an HTML interface or simple status checks:

- **`/defect_table`** (GET): Renders an HTML table of all defects in the database.
- **`/popup_status`** (GET): Checks if the popup window is operational by waiting for a response from the tkinter
  thread.
- **`/server_status`** (GET): Returns the server's operational status and its unique ID.
- **`/controls`** (GET, POST): A web page with troubleshooting controls for the defect popup.
