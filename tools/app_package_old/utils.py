import os
from typing import Optional


def is_py_file(filename: str) -> bool:
    return filename.endswith('.py') and not filename.startswith('__')


def find_image_filename(uid: str, image_folder: str) -> str | None:
    for filename in os.listdir(image_folder):
        if filename.startswith(uid) and filename.endswith(('.png', '.jpg', '.jpeg')):
            return filename
    return None


def find_video_filename(uid: str, video_folder: str, contains: Optional[str] = None) -> str | None:
    for filename in os.listdir(video_folder):
        if filename.startswith(uid) and filename.endswith(('.mp4', '.mov', '.avi')) and (contains is None or contains in filename):
            return filename
    return None
