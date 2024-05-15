import datetime
import logging
from collections import deque
from functools import partial

import flask
import requests
import waitress
from flask_restful import Api

from flask_server_files.queuesholder import queues
from flask_server_files.resources.btn_msg import ButtonMessage
from flask_server_files.resources.database import Database
from flask_server_files.resources.defect import Defect, DefectList
from flask_server_files.resources.lam_operator import Operator
from flask_server_files.resources.signal_popup import Popup
from flask_server_files.routing import routes_blueprint
from flask_server_files.sqla_instance import fsa
from log_and_alert.log_setup import lg
from untracked_config.db_uri import DATABASE_URI
from untracked_config.server_settings import host, port, server_threads

# create and config the flask app
app = flask.Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True  # To allow flask propagating exception even if debug is set to false on app
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'this will be important when security is implemented'
app.debug = True

# add the restful endpoints
api = Api(app)
api.add_resource(Defect, '/defect')
api.add_resource(Popup, '/popup')
api.add_resource(DefectList, '/defects')
api.add_resource(Database, '/database')
api.add_resource(Operator, '/operator')
api.add_resource(ButtonMessage, '/button_msg')

app.register_blueprint(routes_blueprint)


def start_flask_app(in_message_queue=None, out_message_queue=None):
    """Start the flask app with a queue watcher, sqlalchemy, and start the server.

    :param in_message_queue: a queue/deque for incoming messages.
    :param out_message_queue:
    """
    if in_message_queue is not None:
        lg.debug('message queue found!')
        with app.app_context():
            queues.in_message_queue = in_message_queue
            queues.out_message_queue = out_message_queue
            app.in_message_queue = in_message_queue
            app.out_message_queue = out_message_queue
            app.program_unique_id = str(in_message_queue.pop().get('program_unique_id'))
            app.port_check_errors = 0  # for routine check of control of the port
            schedule_queue_watcher(in_message_queue, out_message_queue)
    else:
        lg.warning('No inbound defect_instance queue!')

    fsa.init_app(app)

    waitress.serve(app, host=host, port=port, threads=server_threads)
    lg.debug('after waitress!')


def schedule_queue_watcher(in_message_queue, out_message_queue):
    """Schedules a communications queue watcher to check the inbound queue for requests and send outbound messages.

        :param in_message_queue: collections.deque
        :param out_message_queue: collections.deque
        """

    def regular_check_function():
        # when it's ready, this will watch for requests from the popup (in_message_queue) and send the responses
        # via the out_message_queue
        check_context = app.app_context()
        with check_context:
            while len(in_message_queue):
                lg.debug(f'defect_instance count: %s: , %s', len(in_message_queue), in_message_queue)
                try:
                    msg = in_message_queue.pop()
                    out_message_queue.append({'message': 'hello'})
                    lg.debug('Regular check at %s found a defect_instance: %s', datetime.datetime.now(), msg)

                except IndexError:
                    lg.warning('Index error in while loop. Should never happen.')
                    break  # the deque is empty TODO: the while and try except SHOULD be redundant

    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler(daemon=True, timezone='America/New_York')
    logging.getLogger('apscheduler').setLevel(logging.WARNING)  # don't need to know everything the daemon does
    scheduler.add_job(regular_check_function, 'interval', seconds=10)

    def check_that_port_is_mine(out_bound_messages: deque):
        """Regularly checks the status of the local server port to ensure this program instance is in control.

        This function sends a GET request to the local 'server_status' page to check the status of the local server
        port. It compares the retrieved 'program_unique_id' with the program's own unique ID. If they don't match,
        indicating that another session has control of the port, this instance is aborted.

        If a connection error occurs during the GET request, it indicates that no one has control of the port. In
        this case, the program is restarted.

        Raises:
            RuntimeError: If the retrieved 'program_unique_id' doesn't match the program's own unique ID, indicating
                          another session has control of the port, or if the routine check fails multiple times,
                          leading to program instance shutdown.

        Note: This function is intended to serve as a workaround for an issue where multiple program instances are
        running simultaneously due to an issue that has not been identified.
        """
        # raise RuntimeError("checking how this is handled")
        # todo: the errors get logged, but do not stop anything from running
        #  no sign of these in the logs, though
        # os.abort()  # this shuts the program down without a trace...

        # this looks to leave behind a no longer locked lock file
        # restart_arguments = [sys.executable, sys.executable, *sys.argv]
        # lg.info('restart args: %s', restart_arguments)
        # os.execl(*restart_arguments)

        restart_signal = None
        # restart_signal = RuntimeError('sending restart signal')  # for development

        try:
            response = requests.get(f'http://localhost:{port}/server_status', timeout=8000)
            if response.status_code == 200:
                if response.json().get('server_status').get('program_unique_id') != app.program_unique_id:
                    restart_signal = RuntimeError('Routine check of port control does not have a matching '
                                                  'program_unique_id, another session must have control of the port. '
                                                  'Aborting this instance, now!')
                else:
                    app.port_check_errors = 0
            else:
                lg.warning('Failure during routine check of port control. %s', response)
                app.port_check_errors += 1
                if app.port_check_errors > 3:
                    restart_signal = RuntimeError('Unable to check port control for %d times, shutting down this program '
                                                  'instance, now!', app.port_check_errors)
        except requests.exceptions.ConnectionError as conerr:
            lg.critical('Routine check of port control could not connect. No one has control of the port! Restarting '
                        'program, now! %s', conerr)
            restart_signal = conerr

        if restart_signal:
            out_bound_messages.append({'action': 'restart_popup', 'error': restart_signal})

    scheduler.add_job(partial(check_that_port_is_mine, out_message_queue), 'interval', seconds=10)
    scheduler.start()


@app.teardown_appcontext
def cleanup(resp_or_exc):
    """Clean up sqlalchemy sessions."""

    from flask_server_files.sqla_instance import Session

    Session.remove()


if __name__ == '__main__':
    start_flask_app()
