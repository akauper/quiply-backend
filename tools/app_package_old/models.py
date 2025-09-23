import importlib.util
import mimetypes
import os
from typing import Callable, List, Generic, TypeVar, Dict

from pydantic import BaseModel

from src.models.schemas import Schema
from src.utils import logger
from .constants import IMAGE_URL_ATTR, VIDEO_IDLE_URL_ATTR, VIDEO_INTRO_URL_ATTR
from .utils import is_py_file, find_image_filename, find_video_filename


class TemplateFolders(BaseModel):
    root: str
    active: str
    inactive: str
    images: str
    videos: str


TTemplate = TypeVar('TTemplate', bound=Schema)


class TemplateConfig(BaseModel, Generic[TTemplate]):
    get_existing: Callable[[], List[TTemplate]]
    upload_image: Callable[[str, str, bytes], str]
    upload_video: Callable[[str, str, str, bytes], str]
    folders: TemplateFolders

    def load(self, update_all_images: bool = False) -> List[TTemplate]:
        logger.info(f"Starting to load {self.folders.root}...")

        local_templates = self.load_templates_from_folder(self.folders.active, True)
        # print(local_templates)
        local_templates_list = list(local_templates.values())
        if update_all_images:
            self.update_images(local_templates_list)
            self.update_videos(local_templates_list)
            logger.info(f"Finished loading {self.folders.root}")
            return local_templates_list

        existing_list = self.get_existing()
        existing_templates: Dict[str, TTemplate] = {item.uid: item for item in existing_list}
        needs_image_update_list: List[TTemplate] = []

        for local_key, local_template in local_templates.items():
            existing_template = existing_templates.get(local_key, None)
            if existing_template is None:
                needs_image_update_list.append(local_template)
                continue

            image_url = getattr(existing_template, IMAGE_URL_ATTR, None)
            has_image = image_url is not None and image_url != ""
            if not has_image and local_template.uid not in [item.uid for item in needs_image_update_list]:
                needs_image_update_list.append(local_template)

        self.update_images(needs_image_update_list)
        logger.info(f"Finished loading {self.folders.root}")
        return local_templates_list

    @staticmethod
    def load_templates_from_folder(folder: str, active: bool) -> Dict[str, TTemplate]:
        templates: Dict[str, TTemplate] = {}
        if not os.path.isdir(folder):
            logger.warning(f"Folder {folder} not found.")
            return templates

        for filename in os.listdir(folder):
            if is_py_file(filename):
                try:
                    module_name = filename[:-3]
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(folder, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    template: TTemplate = getattr(module, module_name, None)
                    if template is not None:
                        template.uid = module_name
                        # variable.active = active
                    templates[template.uid] = template
                except Exception as e:
                    logger.error(f"Error loading module {filename}: {e}")
        return templates

    def update_images(self, templates: List[TTemplate]) -> None:
        for template in templates:
            image_filename = find_image_filename(template.uid, self.folders.images)
            if image_filename is not None:
                image_path = os.path.join(self.folders.images, image_filename)
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                content_type, _ = mimetypes.guess_type(image_path)
                image_url = self.upload_image(template.uid, content_type, image_data)
                setattr(template, IMAGE_URL_ATTR, image_url)
            else:
                logger.warning(f"No image found for item {template.uid}")

    def update_videos(self, templates: List[TTemplate]) -> None:
        for template in templates:
            idle_filename = find_video_filename(template.uid, self.folders.videos, 'idle')
            intro_filename = find_video_filename(template.uid, self.folders.videos, 'intro')

            if idle_filename is not None:
                idle_path = os.path.join(self.folders.videos, idle_filename)
                with open(idle_path, 'rb') as f:
                    idle_data = f.read()
                content_type, _ = mimetypes.guess_type(idle_path)
                idle_url = self.upload_video(template.uid, content_type, 'idle', idle_data)
                setattr(template, VIDEO_IDLE_URL_ATTR, idle_url)
            else:
                logger.warning(f"No idle video found for item {template.uid}")

            if intro_filename is not None:
                intro_path = os.path.join(self.folders.videos, intro_filename)
                with open(intro_path, 'rb') as f:
                    intro_data = f.read()
                content_type, _ = mimetypes.guess_type(intro_path)
                intro_url = self.upload_video(template.uid, content_type, 'intro', intro_data)
                setattr(template, VIDEO_INTRO_URL_ATTR, intro_url)
            else:
                logger.warning(f"No intro video found for item {template.uid}")


# import importlib.util
# import os
# from typing import Callable, List
#
# from pydantic import BaseModel
#
# from src.models import Tileable
# from src.utils import logger
# from tools.app_package.constants import IMAGE_URL_ATTR, ATTRIBUTES_TO_IGNORE
# from tools.app_package.utils import is_py_file, find_image_filename
#
#
# class TemplateFolders(BaseModel):
#     root: str
#     active: str
#     inactive: str
#     images: str
#
#
# class TemplateConfig(BaseModel):
#     get_existing: Callable[[], List[Tileable]]
#     update: Callable[[List[Tileable]], None]
#     upload_image: Callable[[str, bytes], str]
#     folders: TemplateFolders
#
#     def load(self, force: bool = False) -> None:
#         logger.info(f"Starting to load {self.folders.root}...")
#         try:
#             existing_items = self.get_existing()
#         except Exception as e:
#             logger.error(f"Error fetching existing items: {e}")
#             return
#
#         active = self.load_variables_from_folder(self.folders.active, True)
#         local_items = active
#
#         needs_update_list: List[Tileable] = []
#
#         for local_item in local_items:
#             existing_item = next((item for item in existing_items if item.uid == local_item.uid), None)
#             if existing_item is None:
#                 logger.info(f"Found new item {local_item.uid}")
#                 self.update_image(local_item)
#                 needs_update_list.append(local_item)
#                 continue
#
#             item_needs_update = self.item_needs_update(local_item, existing_item, force)
#             if item_needs_update and local_item.uid not in [item.uid for item in needs_update_list]:
#                 needs_update_list.append(local_item)
#
#         self.update(needs_update_list)
#
#         logger.info(f"Finished loading {self.folders.root}")
#
#     @staticmethod
#     def load_variables_from_folder(folder: str, active: bool) -> List[Tileable]:
#         variables: List[Tileable] = []
#         if not os.path.isdir(folder):
#             logger.warning(f"Folder {folder} not found.")
#             return variables
#
#         for filename in os.listdir(folder):
#             if is_py_file(filename):
#                 try:
#                     module_name = filename[:-3]
#                     spec = importlib.util.spec_from_file_location(module_name, os.path.join(folder, filename))
#                     module = importlib.util.module_from_spec(spec)
#                     spec.loader.exec_module(module)
#
#                     variable: Tileable = getattr(module, module_name, None)
#                     if variable is not None:
#                         variable.uid = module_name
#                         # variable.active = active
#                     variables.append(variable)
#                 except Exception as e:
#                     logger.error(f"Error loading module {filename}: {e}")
#         return variables
#
#     def update_image(self, item: Tileable) -> None:
#         image_filename = find_image_filename(item.uid, self.folders.images)
#         if image_filename is not None:
#             with open(os.path.join(self.folders.images, image_filename), 'rb') as f:
#                 image_data = f.read()
#                 image_url = self.upload_image(item.uid, image_data)
#                 setattr(item, IMAGE_URL_ATTR, image_url)
#         else:
#             logger.warning(f"No image found for item {item.uid}")
#
#     def item_needs_update(self, local_item: Tileable, existing_item: Tileable, force: bool) -> bool:
#         needs_update = force
#         local_item_dict = local_item.model_dump()  # Convert Pydantic model to dictionary
#         for attr, local_attr_value in local_item_dict.items():
#             if attr in ATTRIBUTES_TO_IGNORE:
#                 continue
#
#             existing_attr_value = getattr(existing_item, attr, None)
#             local_attr_value = getattr(local_item, attr, None)
#             if attr == IMAGE_URL_ATTR:
#                 if force or existing_attr_value is None or existing_attr_value == "":
#                     self.update_image(local_item)
#                     logger.info(f"Updated image for {local_item.uid}")
#                     needs_update = True
#             elif existing_attr_value != local_attr_value:
#                 logger.info(f"""Found difference in {attr} for {local_item.uid}.
#     Local   : {local_attr_value}
#     Existing: {existing_attr_value}""")
#                 needs_update = True
#         return needs_update
