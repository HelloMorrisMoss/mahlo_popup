import json

from flask_restful import reqparse, Resource
from main import dev_popup
from dev_common import get_dummy_dict


class Popup(Resource):
    def __init__(self):
        pass

    def show(self):
        # the laminator is stopped, show the full popup
        # do we want to have this happen automatically? maybe not?
        pass

    def hide(self):
        # the laminator is moving
        pass

    def get(self):
        dev_popup(json.dumps(get_dummy_dict(5.6)))
