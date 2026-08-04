import json
import os
import shutil
import unittest

from help_window.sync_manager import SyncManager
from help_window.utils.cas_manager import get_data_hash


class TestSyncHashBug(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_sync_hash_temp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.content_dir = os.path.join(self.test_dir, "content")
        os.makedirs(self.content_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_json_reserialization_hash_change(self):
        """
        Verify that json.dump/load cycle can change the hash if formatting differs.
        This was the cause of the infinite sync loop.
        """
        original_data = {"a": 1, "b": 2, "c": [1, 2, 3]}
        # Original bytes (no indent, no sort)
        original_bytes = json.dumps(original_data).encode('utf-8')
        original_hash = get_data_hash(original_bytes)

        # Simulated re-serialization with different formatting (e.g. indent)
        reserialized_bytes = json.dumps(original_data, indent=4).encode('utf-8')
        reserialized_hash = get_data_hash(reserialized_bytes)

        self.assertNotEqual(original_hash, reserialized_hash, "Hashes should differ if formatting changes")

        # Verify that our fix (saving raw bytes) preserves hash
        # If we save the bytes directly, the hash stays the same
        with open(os.path.join(self.content_dir, "manifest.json"), "wb") as f:
            f.write(original_bytes)

        with open(os.path.join(self.content_dir, "manifest.json"), "rb") as f:
            saved_bytes = f.read()
            saved_hash = get_data_hash(saved_bytes)

        self.assertEqual(original_hash, saved_hash, "Raw bytes must preserve hash")

    def test_sync_manager_load_hash(self):
        """Verify SyncManager._load_current_version_hash uses raw bytes."""
        original_data = {"files": {"test.json": "hash123"}}
        original_bytes = json.dumps(original_data, indent=2).encode('utf-8')
        original_hash = get_data_hash(original_bytes)

        manifest_path = os.path.join(self.content_dir, "manifest.json")
        with open(manifest_path, "wb") as f:
            f.write(original_bytes)

        sync_mgr = SyncManager(self.content_dir)
        loaded_hash = sync_mgr._load_current_version_hash()

        self.assertEqual(original_hash, loaded_hash)


if __name__ == '__main__':
    unittest.main()
