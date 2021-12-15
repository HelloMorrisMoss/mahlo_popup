import json

from flask import g
from flask_restful import reqparse, Resource

from log_setup import lg


class Popup(Resource):
    def __init__(self):
        pass
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

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True, help='You must provide a command action.')

        data = parser.parse_args()

        if data['action'] == 'shrink':
            g.popup.shrink()
            return {'defect_instance': 'Shrinking popup window.'}, 200

        elif data['action'] == 'show':
            lg.debug('showing popup')
            g.popup.show()
            return {'defect_instance': 'Showing popup window.'}, 200
