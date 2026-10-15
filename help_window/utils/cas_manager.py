import hashlib
import json
import os
import shutil
from typing import Dict, Tuple


def get_file_hash(file_path: str) -> str:
    """Calculates SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_data_hash(data: bytes) -> str:
    """Calculates SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


class CASManager:
    """
    Manages Content-Addressable Storage for help content.
    """

    def __init__(self, content_dir: str):
        self.content_dir = content_dir
        self.blobs_dir = os.path.join(content_dir, "blobs")
        os.makedirs(self.blobs_dir, exist_ok=True)

    def add_file(self, source_path: str) -> str:
        """Adds a file to CAS and returns its hash."""
        file_hash = get_file_hash(source_path)
        dest_path = os.path.join(self.blobs_dir, file_hash)
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
        return file_hash

    def add_data(self, data: bytes) -> str:
        """Adds raw data to CAS and returns its hash."""
        data_hash = get_data_hash(data)
        dest_path = os.path.join(self.blobs_dir, data_hash)
        if not os.path.exists(dest_path):
            with open(dest_path, "wb") as f:
                f.write(data)
        return data_hash

    def get_blob_path(self, blob_hash: str) -> str:
        """Returns the absolute path to a blob by its hash."""
        return os.path.join(self.blobs_dir, blob_hash)

    def create_manifest(self) -> Tuple[str, Dict]:
        """
        Scans content_dir (excluding blobs) and creates a manifest.
        Returns (manifest_hash, manifest_dict).
        """
        manifest = {
            "version": 1,
            "files": {}  # rel_path -> hash
        }

        for root, dirs, files in os.walk(self.content_dir):
            if "blobs" in dirs:
                dirs.remove("blobs")  # Don't recurse into blobs

            for file in files:
                if file == "manifest.json" or file.endswith(".lock"):
                    continue

                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, self.content_dir).replace("\\", "/")
                file_hash = self.add_file(abs_path)
                manifest["files"][rel_path] = file_hash

        manifest_data = json.dumps(manifest, sort_keys=True, indent=2).encode('utf-8')
        manifest_hash = self.add_data(manifest_data)

        # Also save as manifest.json in content_dir for convenience
        with open(os.path.join(self.content_dir, "manifest.json"), "wb") as f:
            f.write(manifest_data)

        return manifest_hash, manifest
