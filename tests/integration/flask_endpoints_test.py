from tests.base_test import BaseTest


class FlaskEndpointsTest(BaseTest):
    def test_defects_endpoint_exists(self):
        with self.app_context():
            response = self.app.get(r'/defects')

            self.assertEqual(response.status_code, 200)

    def test_defects_empty(self):
        with self.app_context():
            response = self.app.get(r'/defects')

            self.assertEqual(response.json, {})
