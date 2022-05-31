"""Contains routing for (human) web interface.

defects_table:  /defect_table renders a simple html view of the defects in the database.

"""
import datetime

import flask

from flask_server_files.resources.defect import DefectList
from log_setup import lg

routes_blueprint = flask.Blueprint('routes', __name__, template_folder='flask_server_files.templates')


@routes_blueprint.route('/defect_table')
def defects_table():
	"""Return an HTML/website for viewing defects.

	:return:
	"""
	import pandas as pd
	return pd.DataFrame.from_dict(DefectList().get()[0]).T.to_html()


@routes_blueprint.route('/popup_status')
def operational_check():
	"""Ask the popup if it is operational."""
	from flask import current_app as app

	# send a request for a popup status report
	app.out_message_queue.append({'action': 'popup_status_check'})
	start_time = datetime.datetime.now()
	mn = 0
	status_received = None

	# wait 5 seconds, while checking for a status message
	while (start_time - datetime.datetime.now()).total_seconds() < 5:
		for mn, msg in enumerate(app.in_message_queue):
			status_received = msg.get('popup_status')

			# ocne a message has been received stop checking
			if status_received:
				break
		if status_received:
			break

	# pop the message from the deque
	p_status = app.in_message_queue[mn]
	del app.in_message_queue[mn]
	lg.debug(p_status)

	return p_status, 200
