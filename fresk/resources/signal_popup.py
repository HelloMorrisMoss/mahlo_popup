from flask_restful import reqparse, Resource

from fresk.queuesholder import queues
from log_setup import lg


class Popup(Resource):
    # def __init__(self):
    #     pass
        # if getattr(g, 'popup') is None:
        #     self.get()
        # self.popup = g.popup

    # def show(self):
    #     import threading
    #
    #     # g.popup_thread = threading.Thread(target=dev_popup)
    #
    #

    #     # the laminator is stopped, show the full popup
    #     # do we want to have this happen automatically? maybe not?
    #     # self.popup
    #     pass
    #
    # def hide(self):
    #     # the laminator is moving
    #     pass
    #
    def get(self):
        # g.popup = dev_popup(json.dumps(get_dummy_dict(5.6)))
        raise NotImplementedError('This had been built with dicts and has not been remade using sqlalchemy version.')

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True, help='You must provide a command action.')

        data = parser.parse_args()
        lg.debug('action received: %s', data['action'])

        if data['action'] == 'shrink':
            queues.out_message_queue.append({'action': 'shrink'})
            return {'popup_result': 'Shrinking popup window.'}, 200

        elif data['action'] == 'show':
            lg.debug('showing popup')
            queues.out_message_queue.append({'action': 'show'})
            return {'popup_result': 'Showing popup window.'}, 200

        elif data['action'] == 'show_force':
            lg.debug('showing popup')
            queues.out_message_queue.append({'action': 'show_force'})
            return {'popup_result': 'Showing popup window (force).'}, 200

        elif data['action'] == 'defects_updated':
            lg.debug('tell popup there are defect updates')
            queues.out_message_queue.append({'action': 'check_defect_updates'})
            return {'popup_result': 'Checking for new defects.'}, 200

        elif data['action'] == 'reset_position':
            lg.debug('tell popup to return to screen origin')
            queues.out_message_queue.append({'action': 'reset_position'})
            return {'popup_result': 'Resetting popup position.'}, 200

        elif data['action'] == 'restart_popup':
            lg.debug('tell popup to restart')
            queues.out_message_queue.append({'action': 'restart_popup'})
            return {'popup_result': 'Restarting popup.'}, 200

        elif data['action'] == 'shift_change':
            lg.debug('tell popup the shift')
            queues.out_message_queue.append({'action': 'shift_change'})
            return {'popup_result': 'Changing shift'}, 200

        else:
            return {'popup_result': 'No valid request.'}, 400
