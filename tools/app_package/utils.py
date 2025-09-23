import mimetypes
from typing import Set, Dict

from src.services import storage_service
from src.models.data import LocalImageMixin
from src.models.app_package import AppPackageData
from src.utils import loggers


def is_py_file(filename: str) -> bool:
    return filename.endswith('.py') and not filename.startswith('__')


def process_local_image_mixins(
        app_package: AppPackageData,
        obj,
        file_path: str,
        firebase_path: str,
        processed: Set[str] = None,
        processed_paths: Dict[str, str] = None
):
    from pydantic import BaseModel

    if processed is None:
        processed = set()

    if processed_paths is None:
        processed_paths = {}

    obj_id = id(obj)
    if obj_id in processed:
        return  # Avoid processing the same object again

    processed.add(obj_id)

    # If the object is a LocalImageMixin, upload its image
    if isinstance(obj, LocalImageMixin):
        upload_image(app_package, obj, file_path, firebase_path, processed_paths)

    # Now, continue to process its attributes in case they contain nested LocalImageMixin instances
    if isinstance(obj, dict):
        for key, value in obj.items():
            process_local_image_mixins(app_package, value, file_path, firebase_path, processed, processed_paths)
    elif isinstance(obj, list):
        for item in obj:
            process_local_image_mixins(app_package, item, file_path, firebase_path, processed, processed_paths)
    elif isinstance(obj, BaseModel):
        # Use the Pydantic model's fields to get data attributes
        for field_name, field_value in obj.__dict__.items():
            process_local_image_mixins(app_package, field_value, file_path, firebase_path, processed, processed_paths)
    # Optionally handle other iterable types (e.g., tuples)
    elif isinstance(obj, tuple):
        for item in obj:
            process_local_image_mixins(app_package, item, file_path, firebase_path, processed, processed_paths)
    else:
        # For other types, you can decide whether to process them or not
        pass


def upload_image(
        app_package: AppPackageData,
        obj: LocalImageMixin,
        file_path: str,
        firebase_path: str,
        processed_paths: Dict[str, str]
):
    if obj.local_image_link:
        obj.image_url = app_package.image_paths[obj.local_image_link]
        return

    local_image_path = obj.local_image_path

    if not local_image_path:
        return obj.image_url or ''

    if local_image_path.startswith('./'):
        local_image_path = file_path + local_image_path[1:]

    if local_image_path in processed_paths:
        obj.image_url = processed_paths[local_image_path]
        return

    try:
        with open(local_image_path, 'rb') as f:
            image_data = f.read()
        content_type = mimetypes.guess_type(local_image_path)[1]

        image_name = obj.local_image_path.split('/')[-1]

        storage_service.delete_media(firebase_path, 'image', metadata_selectors={'fileName': image_name})

        loggers.storage.info(f"Uploading image {image_name} to {firebase_path}...")

        url = storage_service.upload_media(firebase_path, image_name, content_type, 'image', image_data)

        obj.image_url = url
        processed_paths[local_image_path] = url
    except FileNotFoundError:
        loggers.storage.warning(f"Image file not found: {local_image_path}")
        obj.image_url = ''
    except Exception as e:
        loggers.storage.error(f"Error uploading image: {e}")
        obj.image_url = ''
