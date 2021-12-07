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


def start_flask_app():
    fsa.init_app(app)
    host = '0.0.0.0'
    port = 5000
    waitress.serve(app, host=host, port=port, threads=2)
    # app.run(debug=True)


if __name__ == '__main__':
    start_flask_app()