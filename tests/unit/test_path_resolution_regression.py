import json
import os
import shutil
import tempfile
import unittest

from help_window.content_manager import ContentManager


class TestPathResolutionRegression(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.content_dir = os.path.join(self.test_dir, "help_window", "help_content")
        os.makedirs(self.content_dir)
        self.blobs_dir = os.path.join(self.content_dir, "blobs")
        os.makedirs(self.blobs_dir)

        # Create a dummy blob
        self.dummy_content = b"fake image data"
        self.dummy_hash = "dummysha256"
        with open(os.path.join(self.blobs_dir, self.dummy_hash), "wb") as f:
            f.write(self.dummy_content)

        # Create manifest
        self.manifest = {
            "version": 1,
            "files": {
                "media/test_image.png": self.dummy_hash
            }
        }
        with open(os.path.join(self.content_dir, "manifest.json"), "w") as f:
            json.dump(self.manifest, f)

        self.cm = ContentManager(self.content_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_resolve_project_relative_path(self):
        # This simulates how paths appear in the article JSON
        rel_path = "help_window/help_content/media/test_image.png"
        resolved = self.cm.resolve_resource_path(rel_path)

        expected = os.path.join(self.blobs_dir, self.dummy_hash)
        self.assertEqual(os.path.normpath(resolved), os.path.normpath(expected))

    def test_resolve_content_relative_path(self):
        rel_path = "media/test_image.png"
        resolved = self.cm.resolve_resource_path(rel_path)

        expected = os.path.join(self.blobs_dir, self.dummy_hash)
        self.assertEqual(os.path.normpath(resolved), os.path.normpath(expected))

    def test_resolve_absolute_path(self):
        abs_path = os.path.join(self.content_dir, "media", "test_image.png")
        resolved = self.cm.resolve_resource_path(abs_path)

        expected = os.path.join(self.blobs_dir, self.dummy_hash)
        self.assertEqual(os.path.normpath(resolved), os.path.normpath(expected))

    def test_resolve_mixed_slashes(self):
        rel_path = "help_window\\help_content/media\\test_image.png"
        resolved = self.cm.resolve_resource_path(rel_path)

        expected = os.path.join(self.blobs_dir, self.dummy_hash)
        self.assertEqual(os.path.normpath(resolved), os.path.normpath(expected))

    def test_fallback_direct_path(self):
        # Path not in manifest
        rel_path = "media/not_in_manifest.png"
        resolved = self.cm.resolve_resource_path(rel_path)

        expected = os.path.join(self.content_dir, "media", "not_in_manifest.png")
        self.assertEqual(os.path.normpath(resolved), os.path.normpath(expected))


if __name__ == "__main__":
    unittest.main()
