"""Parent class for each non-unit test. Creates and removes a new test table for each test."""

# TODO: integrate creating/removing a database

from unittest import TestCase

from fresk.flask_app import app
from fresk.sqla_instance import fsa


# from flask.ext.testing import TestCase


class BaseTest(TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://tester:tester@localhost:5432/test'
        app.testing = True
        self.app_context = app.app_context
        self.app = app.test_client()

        with self.app_context():
            fsa.init_app(app)
            fsa.create_all()

    def tearDown(self):
        with self.app_context():
            fsa.session.remove()
            fsa.drop_all()
