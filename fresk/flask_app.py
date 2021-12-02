import flask
from flask_restful import Api
from fresk.sqla_instance import fsa

from fresk.resources.defect import Defect
from db_uri import DATABASE_URI

app = flask.Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False # To allow flask propagating exception even if debug is set to false on app
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///localhost:5432'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.secret_key = 'this will be important when security is implemented'

api = Api(app)

@app.before_first_request
def create_tables():
    fsa.create_all()

api.add_resource(Defect, '/defect')

if __name__ == '__main__':
    fsa.init_app(app)
    app.run(debug=True)
