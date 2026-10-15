import json
import os
import shutil
import subprocess
import sys
import time
import unittest

import requests

from help_window.sync_manager import SyncManager


class TestSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.server_content = os.path.join(cls.root_dir, "test_server_content")
        cls.sub_content = os.path.join(cls.root_dir, "test_sub_content")
        cls.db_path = os.path.join(cls.root_dir, "help_versions.db")  # Shared DB for now

        # Cleanup
        for d in [cls.server_content, cls.sub_content]:
            if os.path.exists(d):
                shutil.rmtree(d)
        # We don't necessarily want to delete the main DB if we are running in the repo,
        # but for clean tests we should.
        # Actually, let's just use it and rely on version IDs.

        os.makedirs(cls.server_content, exist_ok=True)
        os.makedirs(cls.sub_content, exist_ok=True)

        # Initial content for server
        cls.article_path = os.path.join(cls.server_content, "test_article.json")
        cls.initial_content = [{"type": "title", "content": "Initial Server Title"}]
        with open(cls.article_path, 'w', encoding='utf-8') as f:
            json.dump(cls.initial_content, f)

    def test_01_full_sync_cycle(self):
        server_port = 5095

        # Start server process using sys.executable to ensure same environment
        server_proc = subprocess.Popen([
            sys.executable, "run_help.py",
            "--headless",
            "--role", "server",
            "--port", str(server_port),
            "--content-dir", self.server_content
        ])

        try:
            # Wait for server to be responsive
            timeout = 30
            start_time = time.time()
            connected = False
            while time.time() - start_time < timeout:
                try:
                    resp = requests.get(f"http://localhost:{server_port}/api/articles", timeout=1)
                    if resp.status_code == 200:
                        connected = True
                        break
                except:
                    pass
                time.sleep(1)

            self.assertTrue(connected, "Server failed to start within timeout")

            auth = ("admin", "password123")

            # 1. Create and Publish Version
            resp = requests.post(f"http://localhost:{server_port}/api/versions/create",
                                 json={"comment": "Test Version 1"}, auth=auth)
            self.assertEqual(resp.status_code, 200, f"Failed to create version: {resp.text}")
            v1 = resp.json()

            resp = requests.post(f"http://localhost:{server_port}/api/versions/publish",
                                 json={"id": v1['id']}, auth=auth)
            self.assertEqual(resp.status_code, 200)

            # 2. Use SyncManager to pull content
            sm = SyncManager(self.sub_content, server_url=f"http://localhost:{server_port}")
            sm._check_for_updates()

            # Verify staging has manifest
            staging_manifest = os.path.join(self.sub_content, "staging", "manifest.json")
            self.assertTrue(os.path.exists(staging_manifest))

            # 3. Apply Update
            success = sm.apply_update()
            self.assertTrue(success)

            # Verify production content
            sub_article = os.path.join(self.sub_content, "test_article.json")
            self.assertTrue(os.path.exists(sub_article))
            with open(sub_article, 'r') as f:
                content = json.load(f)
            self.assertEqual(content[0]['content'], "Initial Server Title")

            # 4. Update and Rollback test
            with open(self.article_path, 'w', encoding='utf-8') as f:
                json.dump([{"type": "title", "content": "Version 2 Title"}], f)

            resp = requests.post(f"http://localhost:{server_port}/api/versions/create",
                                 json={"comment": "Test Version 2"}, auth=auth)
            v2 = resp.json()
            resp = requests.post(f"http://localhost:{server_port}/api/versions/publish",
                                 json={"id": v2['id']}, auth=auth)

            sm._check_for_updates()
            sm.apply_update()

            with open(sub_article, 'r') as f:
                self.assertEqual(json.load(f)[0]['content'], "Version 2 Title")

            # Rollback to v1
            resp = requests.post(f"http://localhost:{server_port}/api/versions/publish",
                                 json={"id": v1['id']}, auth=auth)

            sm._check_for_updates()
            sm.apply_update()

            with open(sub_article, 'r') as f:
                self.assertEqual(json.load(f)[0]['content'], "Initial Server Title")

        finally:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except:
                server_proc.kill()

    @classmethod
    def tearDownClass(cls):
        # Cleanup test directories
        for d in [cls.server_content, cls.sub_content]:
            if os.path.exists(d):
                shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
