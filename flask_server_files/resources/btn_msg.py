from flask_restful import reqparse, Resource

import flask_server_files.queuesholder
from flask_server_files.helpers import remove_empty_parameters


class ButtonMessage(Resource):
    input_parser = reqparse.RequestParser()

    all_args = ('additional_message_text', 'additional_message_clear',
                'set_additional_message_color', 'reset_additional_message_color')
    arg_type_dict = {'additional_message_text': str, 'additional_message_clear': bool,
                     'set_additional_message_color': str, 'reset_additional_message_color': bool,
                     }

    for arg in all_args:
        input_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    input_parser.add_argument('color_theme', type=str, required=False, help='This argument is optional.',
                              choices=('info', 'note', 'warning', 'critical'))

    # the theme color definitions are on the tkinter main window, 'check_for_inbound_messages' method

    def post(self):
        data = self.input_parser.parse_args()

        # don't pass empty parameters
        data = remove_empty_parameters(data)

        action_send_dict = {'action': 'set_additional_msg'}

        if new_txt := data.get('additional_message_text'):
            action_send_dict['additional_message_text'] = new_txt

        if data.get('additional_message_clear'):
            action_send_dict['clear_additional_msg'] = True
            action_send_dict['reset_theme'] = True

        if color_theme := data.get('color_theme'):
            action_send_dict['color_theme'] = color_theme

        if reset_colors := data.get('reset_additional_message_color'):
            action_send_dict['reset_theme'] = reset_colors

        if action_send_dict:
            flask_server_files.queuesholder.queues.out_message_queue.append(action_send_dict)
            response_dict = {'success': True}
            return response_dict, 201
