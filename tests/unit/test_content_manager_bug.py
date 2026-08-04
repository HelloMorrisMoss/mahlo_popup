import json
import os
import shutil
import unittest

from help_window.content_manager import ContentManager


class TestContentManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_content_tmp"
        os.makedirs(self.test_dir, exist_ok=True)

        # Valid article
        with open(os.path.join(self.test_dir, "article1.json"), "w") as f:
            json.dump([{"type": "title", "content": "Article 1"}], f)

        # Manifest (should be ignored)
        with open(os.path.join(self.test_dir, "manifest.json"), "w") as f:
            json.dump({"files": {}}, f)

        # Cache (should be ignored)
        with open(os.path.join(self.test_dir, "help_cache.json"), "w") as f:
            json.dump([], f)

    def test_scan_ignores_manifest_and_cache(self):
        cm = ContentManager(self.test_dir, cache_file="help_cache.json")
        articles = cm.scan_content()

        titles = [a['title'] for a in articles]
        self.assertIn("Article 1", titles)
        self.assertNotIn("manifest", titles)
        self.assertEqual(len(articles), 1)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    unittest.main()
