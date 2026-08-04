import json
import os
from typing import List, Dict

from help_window import lg


class ContentManager:
    """
    Manages loading, parsing, and caching of help article templates.
    """

    def __init__(self, content_dir: str, cache_file: str = "help_cache.json"):
        self.content_dir = content_dir
        self.blobs_dir = os.path.join(content_dir, "blobs")
        self.cache_file = cache_file
        self.articles = []  # List of article metadata
        self.manifest = self._load_manifest()
        self.load_cache()

    def _load_manifest(self) -> Dict:
        manifest_path = os.path.join(self.content_dir, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def resolve_resource_path(self, rel_path: str) -> str:
        """Resolves a relative path to either a blob (if manifest exists) or a local file."""
        if not rel_path:
            return ""

        # Normalize slashes
        path = rel_path.replace("\\", "/")

        # We need to find the path relative to content_dir to look it up in the manifest.
        # rel_path might be absolute, project-relative, or content-relative.

        # 1. Try using absolute paths to identify the prefix (works if CWD is correct)
        abs_rel_path = os.path.abspath(os.path.join(os.getcwd(), path)).replace("\\", "/")
        abs_content_dir = os.path.abspath(self.content_dir).replace("\\", "/")

        search_path = None
        if abs_rel_path.startswith(abs_content_dir + "/"):
            search_path = abs_rel_path[len(abs_content_dir) + 1:]
        elif abs_rel_path == abs_content_dir:
            search_path = ""

        # 2. If no match, try stripping the standard project-relative prefix (fallback for wrong CWD)
        if search_path is None:
            for prefix in ["help_window/help_content/", "./help_window/help_content/"]:
                if path.startswith(prefix):
                    search_path = path[len(prefix):]
                    break

            # 3. If still no match, assume it was already content-relative
            if search_path is None:
                search_path = path

        if self.manifest and "files" in self.manifest:
            blob_hash = self.manifest["files"].get(search_path)
            if blob_hash:
                blob_path = os.path.join(self.blobs_dir, blob_hash)
                if os.path.exists(blob_path):
                    return blob_path
                else:
                    lg.debug(f"Manifest match for {search_path} -> {blob_hash}, but blob missing at {blob_path}")

        # Fallback to direct path in content_dir
        return os.path.join(self.content_dir, search_path)

    def scan_content(self, force: bool = False) -> List[Dict]:
        """
        Scans the content directory for JSON templates and builds the article list.
        Uses cache if available and not forced.
        """
        if self.articles and not force and not self.check_for_updates():
            return self.articles

        articles = []
        if not os.path.exists(self.content_dir):
            lg.error(f"Content directory not found: {self.content_dir}")
            return articles

        for root, dirs, files in os.walk(self.content_dir):
            # Calculate section header from relative folder name
            rel_path = os.path.relpath(root, self.content_dir)
            section = "" if rel_path == "." else rel_path

            for file in files:
                # Ignore manifest.json and the cache file if it happens to be in this directory
                if file.endswith(".json") and file != "manifest.json" and file != os.path.basename(self.cache_file):
                    file_path = os.path.join(root, file)
                    article_meta = self._parse_template_metadata(file_path, section)
                    articles.append(article_meta)

        # Sort articles: section, then title
        articles.sort(key=lambda x: (x['section'], x['title']))
        self.articles = articles
        return articles

    def _parse_template_metadata(self, file_path: str, section: str) -> Dict:
        """
        Parses basic metadata from a template file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = "Untitled"
            is_broken = False

            if isinstance(data, list) and len(data) > 0:
                for block in data:
                    if block.get("type") == "title":
                        title = block.get("content", "Untitled")
                        break
                else:
                    # Fallback to first header if no title block found
                    for block in data:
                        if block.get("type") == "header":
                            title = block.get("content", "Untitled")
                            break
            else:
                is_broken = True
                title = os.path.basename(file_path)

            return {
                "title": title,
                "file_path": file_path,
                "section": section,
                "is_broken": is_broken,
                "mtime": os.path.getmtime(file_path)
            }
        except Exception as e:
            lg.error(f"Error parsing template {file_path}: {e}")
            return {
                "title": os.path.basename(file_path),
                "file_path": file_path,
                "section": section,
                "is_broken": True,
                "mtime": os.path.getmtime(file_path)
            }

    def load_article_content(self, file_path: str) -> List[Dict]:
        """
        Loads the full content of an article.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            lg.error(f"Error loading article {file_path}: {e}")
            return [{"type": "header", "content": "Error"},
                    {"type": "paragraph", "content": "This article is broken. Please contact support."}]

    def save_cache(self):
        """
        Saves the current article list to a cache file.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, indent=4)
        except Exception as e:
            lg.error(f"Error saving cache: {e}")

    def load_cache(self) -> bool:
        """
        Loads the article list from cache. Returns True if successful.
        """
        if not os.path.exists(self.cache_file):
            return False

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
            return True
        except Exception as e:
            lg.error(f"Error loading cache: {e}")
            return False

    def check_for_updates(self) -> bool:
        """
        Checks if any files in content_dir have changed since last scan.
        Only compares file paths and modification times.
        """
        on_disk_files = {}
        for root, dirs, files in os.walk(self.content_dir):
            rel_path = os.path.relpath(root, self.content_dir)
            section = "" if rel_path == "." else rel_path
            for file in files:
                # Ignore manifest.json and the cache file
                if file.endswith(".json") and file != "manifest.json" and file != os.path.basename(self.cache_file):
                    file_path = os.path.join(root, file)
                    on_disk_files[file_path] = os.path.getmtime(file_path)

        if len(on_disk_files) != len(self.articles):
            return True

        for article in self.articles:
            file_path = article.get("file_path")
            if file_path not in on_disk_files or article.get("mtime") < on_disk_files[file_path]:
                return True

        return False

    def _save_to_cache(self, articles: List[Dict]):
        """Internal helper to save a specific list of articles to cache."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=4)
        except Exception as e:
            lg.error(f"Error saving cache: {e}")
