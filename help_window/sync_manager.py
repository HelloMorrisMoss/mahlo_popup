import json
import os
import threading
import time
from typing import Dict, Optional, Callable

import requests

from help_window import lg
from help_window.utils.cas_manager import get_data_hash
from help_window.utils.config import get_settings


class SyncManager:
    """
    Handles background polling and synchronization of help content for subscribers.
    """

    def __init__(self, content_dir: str, on_update_available: Optional[Callable[[str], None]] = None,
                 server_url: str = None):
        self.content_dir = content_dir
        self.blobs_dir = os.path.join(content_dir, "blobs")
        self.staging_dir = os.path.join(content_dir, "staging")
        os.makedirs(self.blobs_dir, exist_ok=True)
        os.makedirs(self.staging_dir, exist_ok=True)

        self.on_update_available = on_update_available
        self.settings = get_settings()
        self.server_url = server_url or self.settings.get("content_server_url", "http://localhost:5005")

        self.base_interval = self.settings.get("sync_interval_base", 60)
        self.max_backoff = self.settings.get("sync_max_backoff", 3600)
        self.current_backoff = self.base_interval

        self.current_version_hash = self._load_current_version_hash()
        self.running = False
        self._thread = None

    def _load_current_version_hash(self) -> Optional[str]:
        manifest_path = os.path.join(self.content_dir, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "rb") as f:
                    return get_data_hash(f.read())
            except Exception:
                return None
        return None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        lg.info(f"SyncManager started. Polling {self.server_url}")
        while self.running:
            try:
                self._check_for_updates()
                # Success, reset backoff
                self.current_backoff = self.base_interval
            except Exception as e:
                lg.error(f"Sync error: {e}. Backing off {self.current_backoff}s")
                # Exponential backoff
                time.sleep(self.current_backoff)
                self.current_backoff = min(self.current_backoff * 2, self.max_backoff)
                continue

            time.sleep(self.current_backoff)

    def _check_for_updates(self):
        response = requests.get(f"{self.server_url}/api/published_version", timeout=10)
        if response.status_code == 200:
            version_info = response.json()
            new_hash = version_info.get("manifest_hash")

            if new_hash != self.current_version_hash:
                lg.info(f"New version available: {new_hash}")
                if self._sync_version(new_hash):
                    if self.on_update_available:
                        self.on_update_available(new_hash)
        elif response.status_code == 404:
            # No published version on server
            pass
        else:
            raise Exception(f"Server returned {response.status_code}")

    def _sync_version(self, manifest_hash: str) -> bool:
        """Downloads manifest and all missing blobs to staging/blobs."""
        try:
            # 1. Download manifest
            m_resp = requests.get(f"{self.server_url}/api/manifest/{manifest_hash}", timeout=10)
            if m_resp.status_code != 200:
                return False

            manifest = m_resp.json()

            # 2. Download missing blobs
            for rel_path, blob_hash in manifest.get("files", {}).items():
                blob_path = os.path.join(self.blobs_dir, blob_hash)
                if not os.path.exists(blob_path):
                    lg.debug(f"Downloading blob {blob_hash} for {rel_path}")
                    b_resp = requests.get(f"{self.server_url}/api/blob/{blob_hash}", timeout=30, stream=True)
                    if b_resp.status_code == 200:
                        with open(blob_path, "wb") as f:
                            for chunk in b_resp.iter_content(chunk_size=8192):
                                f.write(chunk)
                    else:
                        lg.error(f"Failed to download blob {blob_hash}")
                        return False

            # 3. Verify integrity (HLP-040)
            if self.verify_manifest(manifest):
                # Save the new manifest to staging
                staging_manifest = os.path.join(self.staging_dir, "manifest.json")
                with open(staging_manifest, "w") as f:
                    json.dump(manifest, f)
                return True

            return False
        except Exception as e:
            lg.error(f"Error during sync: {e}")
            return False

    def verify_manifest(self, manifest: Dict) -> bool:
        """Full integrity check (HLP-040)."""
        for rel_path, blob_hash in manifest.get("files", {}).items():
            blob_path = os.path.join(self.blobs_dir, blob_hash)
            if not os.path.exists(blob_path):
                return False
            # Optional: verify hash of downloaded file
            if get_file_hash(blob_path) != blob_hash:
                lg.error(f"Integrity check failed for {rel_path} ({blob_hash})")
                return False
        return True

    def apply_update(self) -> bool:
        """
        Applies the update from staging to production.
        Since we use CAS-based loading, 'applying' mostly means updating the manifest.json
        and ensuring all article JSON files are present in content_dir for scanning.
        """
        import shutil
        staging_manifest_path = os.path.join(self.staging_dir, "manifest.json")
        if not os.path.exists(staging_manifest_path):
            return False

        try:
            with open(staging_manifest_path, "r") as f:
                manifest = json.load(f)

            # For JSON articles, we still want them in content_dir so ContentManager can scan them
            # For media, they stay in blobs/
            for rel_path, blob_hash in manifest.get("files", {}).items():
                if rel_path.endswith(".json"):
                    dest_path = os.path.join(self.content_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    blob_path = os.path.join(self.blobs_dir, blob_hash)

                    try:
                        shutil.copy2(blob_path, dest_path)
                    except Exception as e:
                        lg.warning(f"Could not update {rel_path}: {e}")

            # Finalize by moving manifest
            shutil.move(staging_manifest_path, os.path.join(self.content_dir, "manifest.json"))
            self.current_version_hash = self._load_current_version_hash()
            return True
        except Exception as e:
            lg.error(f"Error applying update: {e}")
            return False


def get_file_hash(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


import hashlib
