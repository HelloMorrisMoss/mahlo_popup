"""Contains routing for (human) web interface.

defects_table:  /defect_table renders a simple html view of the defects in the database.

"""
import datetime

import flask
import requests
from flask import request

from flask_server_files.resources.defect import DefectList
from flask_server_files.resources.signal_popup import action_dict
from log_setup import lg
from untracked_config.lam_num import LAM_NUM

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

            # once a message has been received stop checking
            if status_received:
                break
        if status_received:
            break

    # pop the message from the deque
    p_status = app.in_message_queue[mn]
    del app.in_message_queue[mn]
    lg.debug(p_status)

    return p_status, 200


@routes_blueprint.route('/server_status', methods=['GET'])
def server_operational_check():
    """Ask the server if it is operational."""
    from flask import current_app as app

    server_status = {'server_status': {'program_unique_id': app.program_unique_id}}

    return server_status, 200


act_keys = action_dict.keys()


@routes_blueprint.route('/controls', methods=['GET', 'POST'])
def supervisory_controls_page():
    """A web page with troubleshooting controls for the defect popup.

    :return: str, html
    """
    form_response = None
    if request.method == 'GET':
        lg.debug('supervisory page loading.')
    elif request.method == 'POST':  # button pressed
        lg.debug('supervisory page POST RECEIVED')
        for actn in act_keys:  # loop through the button actions and send a request to this web server for the action
            lg.debug('Checking for %s', actn)
            if action_requested := request.form.get(actn):
                lg.debug('Action requested: %s', action_requested)
                form_response = requests.post('http://localhost:5000/popup', json={'action': action_requested})
                if form_response.status_code != 200:
                    lg.warn(f'Action post error: {form_response.__dict__=}')
    return flask.render_template('pop_up_supervisory_controls.html', action_list=act_keys, action_dict=action_dict,
                                 lam_num=LAM_NUM, form_response=form_response)
