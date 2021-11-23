10/29 todo:

* find out from Jeff/operators what should go on the popup, ex: change length removed?
* write the 'saved' results locally, probably sqlite3 db.
  * then try to send all unsent results to the oee db.

11/08 todo:

* what version of python is already on the Mahlo HMI?
  * lam1 & 2 have Python 3.3.5
  * what version can Windows 7 (compact edition) run?
    * it looks like up to but not including 3.9 - so 3.8.7
* different numbers of rolls can be made, need to make the display able to handle that

11/09 to 11/23 todo:
* RPC options compared
  * tests built and evaluated.
  * RPyC looks like the option for this project.
* Now able to call the Popup using RPyC.
* The Popup has the following improvements:
  * No maximize/minimize buttons.
  * Popup stays on top.
  * When switching to another window, Popup shrinks down to a button. When the button is pressed, restores the messages.

11/23 todo:
* build the messages database on the oee.
* add testing data.
* build connection for Popup server.
* test Popup with database.

future:
* The save button needs to save the message to the sqlite database.
  * The server needs to regularly check for messages that have been saved and report back to the postgres db.
  * The operators need to be able to create messages and add/change the reason for removal.
  * The operators need to be able to edit recently saved messages in case they made a mistake.
  * Roll destroyed button... would require knowing the length of the rolls. (Wait was this the source or finished roll?)
* RPyC is pure Python, so it should be able to run inside Ignition.
  * install on the gateway.
  * test.
  * import the client/code into Ignition gateway.
* if it cannot work within Ignition, an intermediate server will need to either:
  * listen for some message from ignition.
  * watch the database for new messages and for the Mahlo being stopped.
* Ignition will need to collect the data and put it in the database.
  * Possibly signal that there are new messages.
  * Possibly signal that the Mahlo is running or not running.
