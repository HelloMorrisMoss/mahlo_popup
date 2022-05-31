import datetime
import logging

import flask
import waitress
from flask_restful import Api

from flask_server_files.queuesholder import queues
from flask_server_files.resources.database import Database
from flask_server_files.resources.defect import Defect, DefectList
from flask_server_files.resources.lam_operator import Operator
from flask_server_files.resources.signal_popup import Popup
from flask_server_files.routing import routes_blueprint
from flask_server_files.sqla_instance import fsa
from log_setup import lg
from untracked_config.db_uri import DATABASE_URI

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
            schedule_queue_watcher(in_message_queue, out_message_queue)
    else:
        lg.warning('No inbound defect_instance queue!')

    fsa.init_app(app)

    host = '0.0.0.0'  # accessible to outside connections
    port = 5000
    waitress.serve(app, host=host, port=port, threads=2)
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
    scheduler.start()


@app.teardown_appcontext
def cleanup(resp_or_exc):
    """Clean up sqlalchemy sessions."""

    from flask_server_files.sqla_instance import Session

    Session.remove()


if __name__ == '__main__':
    start_flask_app()
