from flask_restful import reqparse, Resource

from flask_server_files.helpers import remove_empty_parameters


class ButtonMessage(Resource):
    defect_parser = reqparse.RequestParser()

    all_args = ('lot_number', 'additional_message_text', 'button_color')
    arg_type_dict = {'lot_number': str, 'additional_message_text': str, 'button_color': str}

    for arg in all_args:
        defect_parser.add_argument(arg, type=arg_type_dict[arg], required=False, help='This argument is optional.')

    def post(self):
        data = self.defect_parser.parse_args()

        # don't pass the Model empty parameters
        data = remove_empty_parameters(data)

        from flask_server_files.queuesholder import queues

        queues.out_message_queue.append({'action': 'set_additional_msg',
                                         'additional_message_text': data['additional_message_text'],
                                         'button_color': 'warning'
                                         },
                                        
                                        )

        response_dict = {'success': True}
        return response_dict, 201
