import datetime

import flask
import waitress
from flask import g
from flask_restful import Api

from fresk.queuesholder import queues
from fresk.resources.database import Database
from fresk.resources.defect import Defect, DefectList
from fresk.resources.signal_popup import Popup
from fresk.routing import routes_blueprint
from fresk.sqla_instance import fsa
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

app.register_blueprint(routes_blueprint)


def start_flask_app(in_message_queue=None, out_message_queue=None):
    """Start the flask app with a queue watcher, sqlalchemy, and start the server.

    :param in_message_queue: a queue/deque for incoming messages.
    :param out_message_queue:
    """
    if in_message_queue is not None:
        app_context = app.app_context()
        with app_context:
            queues.in_message_queue = in_message_queue
            queues.out_message_queue = out_message_queue
            g.in_message_queue = in_message_queue
            g.out_message_queue = out_message_queue
            g.out_message_queue.append({'flask_app': app})
            schedule_queue_watcher(in_message_queue, out_message_queue)
    else:
        lg.warning('No inbound defect_instance queue!')

    fsa.init_app(app)

    host = '0.0.0.0'
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
                print(f'defect_instance count: {len(in_message_queue)}')
                print(in_message_queue)
                try:
                    msg = in_message_queue.pop()
                    out_message_queue.append({'message': 'hello'})
                    lg.debug(f'Regular check at {datetime.datetime.now()} found a defect_instance: {msg}')
                except IndexError:
                    break  # the deque is empty TODO: the while and try except SHOULD be redundant

    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler(daemon=True, timezone='America/New_York')
    scheduler.add_job(regular_check_function, 'interval', seconds=10)
    scheduler.start()


if __name__ == '__main__':
    start_flask_app()
