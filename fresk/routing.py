import flask

from fresk.flask_app import app
from fresk.resources.defect import DefectList

routes_blueprint = flask.Blueprint('routes', __name__, template_folder='fresk.templates')


@routes_blueprint.route('/defect_table')
def defects_table():
	"""Return an HTML/website for viewing defects.

	:return:
	"""
	import pandas as pd
	with app.app_context():
		return pd.DataFrame.from_dict(DefectList().get()[0]).T.to_html()
