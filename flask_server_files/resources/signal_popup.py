from flask_restful import reqparse, Resource

from flask_server_files.queuesholder import queues
from log_setup import lg

action_dict = {
    'shrink':
        {'debug_message': 'shrinking popup',
         'action_params': {'action': 'shrink'},
         'return_result': ({'popup_result': 'Shrinking popup window.'}, 200),
         'description': 'Shrink the window to button size, no change if already button.',
         },
    'show':
        {'debug_message': 'showing popup',
         'action_params': {'action': 'show'},
         'return_result': ({'popup_result': 'Showing popup window.'}, 200),
         'description': 'Show the full window if there are defects active, no change if already full.',
         },
    'show_force': {
        'debug_message': 'showing popup',
        'action_params': {'action': 'show_force'},
        'return_result': ({'popup_result': 'Showing popup window (force).'}, 200),
        'description': 'Show the full window even if no defects active, no change if already full.',
        },
    'defects_updated': {
        'debug_message': 'tell popup there are defect updates',
        'action_params': {'action': 'check_defect_updates'},
        'return_result': ({'popup_result': 'Checking for new defects.'}, 200),
        'description': 'Tell the window to check for updates to the defects in the database.',
        },
    'reset_position':
        {'debug_message': 'tell popup to return to screen origin',
         'action_params': {'action': 'reset_position'},
         'return_result': ({'popup_result': 'Resetting popup position.'}, 200),
         'description': 'Return the window to the top left corner of the screen.',
         },
    'restart_popup':
        {'debug_message': 'tell popup to restart',
         'action_params': {'action': 'restart_popup'},
         'return_result': ({'popup_result': 'Restarting popup.'}, 200),
         'description': 'Close the popup program entirely (including the web server) and start it again.',
         },
    'shift_change': {
        'debug_message': 'tell popup the shift',
        'action_params': {'action': 'shift_change'},
        'return_result': ({'popup_result': 'Changing shift'}, 200),
        'description': 'Tell the popup that a shift change is happening, resetting the operator selected to "NO '
                       'OPERATOR".',
        }}


class Popup(Resource):

    def get(self):
        # g.popup = dev_popup(json.dumps(get_dummy_dict(5.6)))
        raise NotImplementedError('This had been built with dicts and has not been remade using sqlalchemy version.')

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True, help='You must provide a command action.')
        # parser.add_argument('source', type=str, required=True, help='You must provide a command action.')

        data = parser.parse_args()
        lg.debug('action received: %s', data['action'])

        action_to_take = action_dict.get(data['action'])
        if action_to_take is not None:
            lg.debug('Action to take: %s', action_to_take)
            if db_msg := action_to_take.get('debug_message') is not None:
                lg.debug(db_msg)
            queues.out_message_queue.append(action_to_take['action_params'])
            return action_to_take['return_result']
        else:
            lg.debug('Did not receive a valid action.')
            return {'popup_result': 'No valid request.'}, 400
