from collections import deque
from threading import Thread
import flask
from flask import g
from flask_restful import Api
import waitress

from fresk.resources.signal_popup import Popup
from fresk.sqla_instance import fsa

from fresk.resources.defect import Defect, DefectList
from db_uri import DATABASE_URI
# from main import dev_popup

from log_setup import lg

app = flask.Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True  # To allow flask propagating exception even if debug is set to false on app
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'this will be important when security is implemented'
app.debug = True

api = Api(app)


# def start_popup():
#


@app.before_first_request
def create_tables():
    fsa.create_all()
    # g.popup_thread = Thread(target=dev_popup)
    # g.popup = dev_popup()


# @app.before_first_request
# def create_popup():
#     g.popup = dev_popup()

api.add_resource(Defect, '/defect')
api.add_resource(Popup, '/popup')
api.add_resource(DefectList, '/defects')


def start_flask_app(in_message_queue=None, out_message_queue=None):
    if in_message_queue is not None:
        schedule_queue_watcher(in_message_queue, out_message_queue)
    else:
        lg.warning('No inbound message queue!')

    fsa.init_app(app)
    host = '0.0.0.0'
    port = 5000
    waitress.serve(app, host=host, port=port, threads=2)


def schedule_queue_watcher(in_message_queue, out_message_queue):
    """Schedules a communications queue watcher to check the inbound queue for requests and send outbound messages.

        :param in_message_queue: collections.deque
        :param out_message_queue: collections.deque
        """
    import time
    def regular_check_function():
        # when it's ready, this will watch for requests from the popup (in_message_queue) and send the responses
        # via the out_message_queue
        import datetime
        while len(in_message_queue):
            print(f'message count: {len(in_message_queue)}')
            print(in_message_queue)
            try:
                msg = in_message_queue.pop()
                lg.debug(f'Regular check at {datetime.datetime.now()} found a message: {msg}')
                out_message_queue.append(f'I got the message "{msg}"!')
            except IndexError:
                break  # the deque is empty TODO: the while and try except SHOULD be redundant
            time.sleep(10)

    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(regular_check_function, 'interval', seconds=30)
    scheduler.start()


if __name__ == '__main__':
    start_flask_app()
