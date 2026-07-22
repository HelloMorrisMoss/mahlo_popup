import json
import os
import shutil
import tempfile
import unittest

from help_window.content_manager import ContentManager


class TestContentManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for help content
        self.test_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.test_dir, "test_cache.json")
        self.cm = ContentManager(self.test_dir, self.cache_file)

        # Create some test articles
        self.article1_path = os.path.join(self.test_dir, "article1.json")
        with open(self.article1_path, "w") as f:
            json.dump([{"type": "header", "content": "Article 1"}], f)

        # Create a subfolder with an article
        self.subfolder = os.path.join(self.test_dir, "Section A")
        os.mkdir(self.subfolder)
        self.article2_path = os.path.join(self.subfolder, "article2.json")
        with open(self.article2_path, "w") as f:
            json.dump([{"type": "header", "content": "Article 2"}], f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scan_content(self):
        articles = self.cm.scan_content()
        self.assertEqual(len(articles), 2)

        # Verify section headers
        # article1.json is in root, relpath is "." -> section ""
        # article2.json is in "Section A", relpath is "Section A" -> section "Section A"

        titles = [a["title"] for a in articles]
        self.assertIn("Article 1", titles)
        self.assertIn("Article 2", titles)

        sections = [a["section"] for a in articles]
        self.assertIn("", sections)
        self.assertIn("Section A", sections)

    def test_title_block_priority(self):
        """Verify that 'title' block takes priority over 'header' block for metadata."""
        priority_path = os.path.join(self.test_dir, "priority.json")
        with open(priority_path, "w") as f:
            json.dump([
                {"type": "title", "content": "The Real Title"},
                {"type": "header", "content": "A Fake Title"}
            ], f)

        articles = self.cm.scan_content(force=True)
        priority_article = next(a for a in articles if a["file_path"] == priority_path)
        self.assertEqual(priority_article["title"], "The Real Title")

    def test_caching(self):
        self.cm.scan_content()
        self.cm.save_cache()

        self.assertTrue(os.path.exists(self.cache_file))

        # New manager instance to load from cache
        new_cm = ContentManager(self.test_dir, self.cache_file)
        success = new_cm.load_cache()
        self.assertTrue(success)
        self.assertEqual(len(new_cm.articles), 2)
        self.assertEqual(new_cm.articles[0]["title"], self.cm.articles[0]["title"])

    def test_broken_template(self):
        broken_path = os.path.join(self.test_dir, "broken.json")
        with open(broken_path, "w") as f:
            f.write("invalid json")

        articles = self.cm.scan_content()
        broken_article = next(a for a in articles if a["file_path"] == broken_path)
        self.assertTrue(broken_article["is_broken"])

    def test_check_for_updates(self):
        self.cm.scan_content()
        self.assertFalse(self.cm.check_for_updates())

        # Modify a file
        import time
        time.sleep(0.1)  # Ensure mtime changes
        with open(self.article1_path, "w") as f:
            json.dump([{"type": "header", "content": "Article 1 Updated"}], f)

        self.assertTrue(self.cm.check_for_updates())


if __name__ == "__main__":
    unittest.main()
