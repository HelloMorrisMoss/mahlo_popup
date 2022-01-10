from base_test import BaseTest


class TestFlask(BaseTest):
	def test_something(self):
		with self.flask_app() as flask_client:
			response = flask_client.get(r'/defects')

			self.assertEqual(response.status_code, 200)
