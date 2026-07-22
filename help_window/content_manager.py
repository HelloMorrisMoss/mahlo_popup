import json
import logging
import os
from typing import List, Dict

lg = logging.getLogger(__name__)


class ContentManager:
    """
    Manages loading, parsing, and caching of help article templates.
    """

    def __init__(self, content_dir: str, cache_file: str = "help_cache.json"):
        self.content_dir = content_dir
        self.cache_file = cache_file
        self.articles = []  # List of article metadata
        self.load_cache()

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
                if file.endswith(".json"):
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
                if file.endswith(".json"):
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
