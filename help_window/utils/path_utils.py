import os


def resolve_resource_path(file_path: str) -> str:
    """
    Resolves a file path for help resources (images/videos).
    Checks absolute path, then relative to current working directory.
    Returns the absolute path if found, otherwise returns original path.
    """
    if not file_path:
        return ""

    # If it's already an absolute path and exists
    if os.path.isabs(file_path) and os.path.isfile(file_path):
        return file_path

    # Try relative to CWD (project root)
    abs_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
    if os.path.isfile(abs_path):
        return abs_path

    return file_path
