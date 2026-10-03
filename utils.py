# utils.py
"""
Utility functions for file extension validation, unique naming, and cleanup.
"""
import os
import uuid


def check_extension(filename, allowed_set):
    """Check if the given filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


def get_file_extension(filename):
    """Extract lowercase file extension without dot."""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def generate_unique_filename(prefix, extension):
    """Generate a unique filename using UUID4."""
    uid = uuid.uuid4().hex
    clean_ext = extension.lstrip(".")
    return f"{prefix}_{uid}.{clean_ext}"


def cleanup_files(*paths):
    """Safely remove temporary files if they exist."""
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
