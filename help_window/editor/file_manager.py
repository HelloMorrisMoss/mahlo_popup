import json
import os
import shutil
from typing import List, Dict

from help_window import lg


def update_all_references(content_dir: str, old_path: str, new_path: str):
    """
    Scans all JSON articles in content_dir and updates any references from old_path to new_path.
    Paths should be relative to project root (as they appear in JSON).
    """
    # Normalize paths to use forward slashes
    old_path = old_path.replace("\\", "/")
    new_path = new_path.replace("\\", "/")

    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                changed = False

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    lg.error(f"Error reading {file_path} for reference update: {e}")
                    continue

                if not isinstance(data, list):
                    continue

                for block in data:
                    # Check 'content' (media)
                    if block.get("type") in ["image", "video"]:
                        content = block.get("content", "")
                        if content == old_path:
                            block["content"] = new_path
                            changed = True
                        elif content.startswith(old_path + "/"):
                            block["content"] = content.replace(old_path + "/", new_path + "/", 1)
                            changed = True

                    # Check 'target' (links)
                    if block.get("type") == "link":
                        target = block.get("target", "")
                        if target == old_path:
                            block["target"] = new_path
                            changed = True
                        elif target.startswith(old_path + "/"):
                            block["target"] = target.replace(old_path + "/", new_path + "/", 1)
                            changed = True

                if changed:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4)
                        lg.info(f"Updated references in {file_path}")
                    except Exception as e:
                        lg.error(f"Error writing {file_path} after reference update: {e}")


def rename_resource(project_root: str, old_abs_path: str, new_name: str):
    """
    Renames a file or folder and updates all references in the help system.
    """
    if not os.path.exists(old_abs_path):
        raise FileNotFoundError(f"Source path not found: {old_abs_path}")

    parent_dir = os.path.dirname(old_abs_path)
    new_abs_path = os.path.join(parent_dir, new_name)

    if os.path.exists(new_abs_path):
        raise FileExistsError(f"Target path already exists: {new_abs_path}")

    # Calculate relative paths for reference updates
    try:
        old_rel = os.path.relpath(old_abs_path, project_root).replace("\\", "/")
        new_rel = os.path.relpath(new_abs_path, project_root).replace("\\", "/")
    except ValueError:
        # Fallback if paths are on different drives or something
        old_rel = old_abs_path
        new_rel = new_abs_path

    # Perform rename
    os.rename(old_abs_path, new_abs_path)

    # Update references in all articles
    content_dir = os.path.join(project_root, "help_window", "help_content")
    update_all_references(content_dir, old_rel, new_rel)

    return new_abs_path


def delete_resource(project_root: str, abs_path: str):
    """
    Deletes a file or folder.
    """
    if os.path.isfile(abs_path):
        os.remove(abs_path)
    elif os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
    else:
        raise FileNotFoundError(f"Path not found: {abs_path}")


def get_media_dir(project_root: str, article_path: str) -> str:
    """
    Determines the appropriate media directory for an article.
    Help content is in project_root/help_window/help_content/.
    Returns the absolute path to the media directory.
    """
    content_dir = os.path.join(project_root, "help_window", "help_content")

    if not article_path:
        media_dir = os.path.join(content_dir, "media")
        if not os.path.exists(media_dir):
            os.makedirs(media_dir, exist_ok=True)
        return media_dir

    # If article_path is a directory (e.g. from EditorManager), use it as base
    if os.path.isdir(article_path):
        base_dir = article_path
    else:
        base_dir = os.path.dirname(article_path)

    try:
        rel_to_content = os.path.relpath(base_dir, content_dir)
    except ValueError:
        # Article is on a different drive or something
        rel_to_content = "."

    parts = rel_to_content.split(os.sep)
    if parts and parts[0] != ".." and parts[0] != ".":
        # Article is in a subfolder of help_content
        top_level_folder = os.path.join(content_dir, parts[0])
        media_dir = os.path.join(top_level_folder, "media")
    else:
        # Article is at the root of help_content
        media_dir = os.path.join(content_dir, "media")

    if not os.path.exists(media_dir):
        os.makedirs(media_dir, exist_ok=True)

    return media_dir


def upload_media(project_root: str, article_path: str, source_file: str) -> str:
    """
    Copies a source media file to the article's media directory.
    Returns the path relative to the project root, using forward slashes.
    """
    media_dir = get_media_dir(project_root, article_path)
    filename = os.path.basename(source_file)
    dest_path = os.path.join(media_dir, filename)

    # If file already exists and is different, we might want a suffix
    # But for now, let's keep it simple.
    if os.path.abspath(source_file) != os.path.abspath(dest_path):
        shutil.copy2(source_file, dest_path)

    rel_path = os.path.relpath(dest_path, project_root).replace("\\", "/")
    return rel_path


def move_resource(project_root: str, old_abs_path: str, new_parent_dir: str):
    """
    Moves a file or folder to a new parent directory and updates all references.
    """
    if not os.path.exists(old_abs_path):
        raise FileNotFoundError(f"Source path not found: {old_abs_path}")
    if not os.path.isdir(new_parent_dir):
        raise NotADirectoryError(f"Target is not a directory: {new_parent_dir}")

    name = os.path.basename(old_abs_path)
    new_abs_path = os.path.join(new_parent_dir, name)

    if os.path.exists(new_abs_path):
        raise FileExistsError(f"Target path already exists: {new_abs_path}")

    # Calculate relative paths for reference updates
    try:
        old_rel = os.path.relpath(old_abs_path, project_root).replace("\\", "/")
        new_rel = os.path.relpath(new_abs_path, project_root).replace("\\", "/")
    except ValueError:
        old_rel = old_abs_path
        new_rel = new_abs_path

    # Perform move
    shutil.move(old_abs_path, new_abs_path)

    # Update references in all articles
    content_dir = os.path.join(project_root, "help_window", "help_content")
    update_all_references(content_dir, old_rel, new_rel)

    return new_abs_path


def consolidate_article_media(project_root: str, article_path: str, data: List[Dict]) -> (List[Dict], bool):
    """
    Ensures all media referenced in the article data is stored in the 
    article's designated category-specific media folder.
    Returns (updated_data, changed_flag).
    """
    changed = False
    new_data = []

    for block in data:
        new_block = block.copy()
        if block.get("type") in ["image", "video"]:
            content = block.get("content", "")
            if content:
                # Get the absolute path of the current media
                # Some paths might be already relative to project root
                if os.path.isabs(content):
                    abs_source = content
                else:
                    abs_source = os.path.abspath(os.path.join(project_root, content))

                if os.path.exists(abs_source):
                    # Upload it to the "correct" folder
                    new_rel_path = upload_media(project_root, article_path, abs_source)
                    if new_rel_path != content.replace("\\", "/"):
                        new_block["content"] = new_rel_path
                        changed = True

        new_data.append(new_block)

    return new_data, changed
