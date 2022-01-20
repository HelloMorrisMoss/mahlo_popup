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

12/7 todo:
  * previously in future:
    * RPyC is pure Python, so it should be able to run inside Ignition.
      * install on the gateway.
      * test.
      * import the client/code into Ignition gateway.
    * (new) there was incompatibility issues with Python2/3 RPyC (for Ignition/Popup)
      * if it cannot work within Ignition, an intermediate server will need to either:
        * listen for some message from ignition.
        * watch the database for new messages and for the Mahlo being stopped.
      * (new) built a flask server that would run as part of the popup program.
        * would directly interact with the database (sqlalchemy).
        * would be easy to signal using http/flask RESTful api.
  * today:
    * refactored Popup to be more OO and fixed a number of issues.
      * fixed: message display label missing.
      * fixed: popup could not display without defect 'messages'.
      * add an 'add removal' button.
      * add change removal reason button/selector.

future:
* The save button needs to save the message to the sqlite database.
  * The server needs to regularly check for messages that have been saved and report back to the postgres db.
  * The operators need to be able to create messages and add/change the reason for removal.
  * The operators need to be able to edit recently saved messages in case they made a mistake.
  * Roll destroyed button... would require knowing the length of the rolls. (Wait was this the source or finished roll?)

* Ignition will need to collect the data and put it in the database.
  * Possibly signal that there are new messages.
  * Possibly signal that the Mahlo is running or not running.

* the flask server and tkinter (popup) threads must communicate in some way.

12/8 todo:

popup needs to:
* grow/shrink when needed
  * shrink when the lam starts
    * to signal this, could use flask server
      * communicate via queue?
    * could use sqlalchemy to watch a table for whether the lam is running
      * maybe the Timescale history (this makes me nervous, how to readonly?)
      * a table in the report database that just holds this value
  * shrink when some 'shrink' button is hit
  * grow when the show messages button is hit
* load new defect records from the database
  * could use sqlalchemy directly
  * could use requests to ask flask server for records
* update the database when the defects are changed
  * could use sqlalchemy directly
  * could use requests to ask flask server for records

12/10 todo:
* add defect button works but the window doesn't seem to resize for its message panels. fixed
* defect type selection screen
* have defect types show in message window
* popup: on creation single defect is being displayed twice - fixed
* popup: when creating new message panels at creation, extra window showing - fixed
* need to be able to change the length of the defect - done
* selecting the save and add new defect buttons are triggering the focus lost shrink - fixed
* need to test on a laminator
* need to build the Ignition end of things - done
* shrink/grow messages from flask to the popup need to be setup, both ends
* need to test if new records can populate the defect message window while 'hidden'
* the show defects button count isn't updating, need to have that as probably a tk.IntVar (if not already) and update it
  when the defect list updates
* when the defects save and the defects are removed from the current list, does that have a loop that isn't breaking
  after finding the defect (not a big deal here, but not ideal)

Ignition end of things brainstorming:
* need to determine when defects have started and ended
  * mahlo "out of spec" tag
* need to create a new defect record, options:
  * directly in the database
  * RESTful call to popup/flask server on Mahlo HMI (would this allow not needing start/stop calls? I think no)
  * call to another flask server on the OEE using the same DefectModel/SQLalchemy
  * other?
* need to signal that the laminator is starting and stopping
  * this is what the flask server was for initially, use post/put to send a json message indicating start or stop
    * how long between start/stop and the popup shows the change? (I think on the tkinter end the queue check can be
      scheduled in ms)

12/15 todo:

* new defect needs to get current values from tag history database (or if we get the webdev module, from Ignition)
* a new defect in an open window, the window needs to resize to accommodate - done
* new defect button may be adding multiple new defects? fixed

12/16 todo:

* replace the message label with a tk.Text so that the important bits can be bolded
* need the basic functionality for defect reason popup. fixed

12/20 todo:

* the default timestamps may be a specific time when now() ran (table creation) not the function at the time the row is
  created - fixed

12/21 todo:

* get rid of the extra windows- fixed

12/22

* the popup needs to show defects only for that laminator
* count button needs a larger font
* install on a mahlo hmi to test
* select attributes still shows next to rolls/save
* OK button on select attributes needs to look better
* the current selection on select attributes need to be 'accent'ed when loading a defect
* save button should be larger
* there is a cancel button on the type of defect panel - it needs to be removed

12/24 todo:

* reopening the set attribute panel, the ok button errors: .!defectmessageframe.!messagepanel2.!frame - fixed

01/04 todo:

* changes panel is still not hiding the toggles.
* test on a Mahlo HMI pc
* save button should be larger
* count button needs a larger font
* the popup needs to show defects only for that laminator

01/10 todo:

* determine if the current defect detection is working, else what needs to be done
  * length calculation is not, created a new calculation using the lam speed between the defect start/stop, testing
  * not consistently seeing defect start length match up
* the MDS sheet is also used to record destroyed rolls, will need something for that in the popup
* need to talk to production about current scrap recording and what happens with the extra foam at thickness changeover
  * they record scrap in an excel sheet
  * there in theory is practically no thickness changeover scrap
* the **MdValProfilMax** and **MdValProfilMin** Mahlo tags look like they may be the last scan max/min for the Mahlo
  * can we use those with the primary/secondary/tertiary criteria as per the export project to determine when to auto
    generate a defect?

01/14 todo:

* what needs to go into the destroyal panel/record
  * lot number
  * reason
  * length?
  * thickness?
* options
  * create new SQLAlchemy model/Flask resource etc.
  * use the new defect panel with some modifications and record it as a defect

01/17 todo:

* if using the new defect popup:
  * need an option to change the lot #, should they desire to record destroying a roll that is not current.
  * set up for recording that defects have been included in a report
    * add a column for included_in_report_file_id
    * add a table for files that a defect has been included in, we may desire it to be included in more than one (end
      length)

01/20 todo:

* web interface for supervisors etc with hyperlinks for show, hide, etc.