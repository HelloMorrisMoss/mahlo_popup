# from unittest import TestCase
from flask.ext.testing import TestCase

from fresk.flask_app import app


class BaseTest(TestCase):
	def setUp(self):
		app.testing = True
		self.flask_app = app.test_client
