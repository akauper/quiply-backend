import mimetypes
import os.path
from typing import Any, Tuple, List, Dict

from devtools import debug
from pydantic import ValidationError

from src.models.app_package import AppPackageData, AppPackage
from src.models import LobbyTreeSchema, ScenarioSchema, ActorSchema
from src.services import storage_service
from src.utils import logger
from .models import TemplateConfig
from .utils import process_local_image_mixins
from ..base_tool import BaseTool
from .constants import APP_PACKAGE_PATH

remote_version = storage_service._fetch_remote_app_package_version()
if not remote_version:
    remote_version = 0
remote_data = storage_service._fetch_remote_app_package_data()


LOBBY_TREE = TemplateConfig[LobbyTreeSchema](
    root_folder="lobby_tree",
    attribute_name="lobby_tree",
    model_class=LobbyTreeSchema,
)

SCENARIO_TEMPLATES = TemplateConfig[ScenarioSchema](
    root_folder="scenarios",
    attribute_name="scenario_templates",
    model_class=ScenarioSchema,
)

ACTOR_TEMPLATES = TemplateConfig[ActorSchema](
    root_folder="actors",
    attribute_name="actor_templates",
    model_class=ActorSchema,
)


class AppPackageTool(BaseTool):
    def run_all(self, **kwargs) -> None:
        force = kwargs.get("force", False)
        no_images = kwargs.get("no_images", False)

        logger.info(f"Running Tool AppPackageTool with force={force}...")

        if not os.path.isdir(APP_PACKAGE_PATH):
            raise FileNotFoundError(f"Folder {APP_PACKAGE_PATH} not found.")

        try:
            app_package: AppPackageData = AppPackageData(
                version=remote_version + 1,
            )

            # if remote_data and no_images:
            #     image_paths = remote_data.image_paths
            # else:
            #     image_paths = self.upload_images()

            image_paths = self.upload_images()
            app_package.image_paths = image_paths

            lobby_tree = LOBBY_TREE.load_data_list()
            scenario_templates = SCENARIO_TEMPLATES.load_data_list()
            actor_templates = ACTOR_TEMPLATES.load_data_list()

            LOBBY_TREE.process_data_list(app_package, lobby_tree, None)
            SCENARIO_TEMPLATES.process_data_list(app_package, scenario_templates, None)
            ACTOR_TEMPLATES.process_data_list(app_package, actor_templates, None)

            app_package.lobby_tree = lobby_tree[0] if lobby_tree else None
            app_package.scenarios = scenario_templates
            app_package.actors = actor_templates

            debug(app_package)
        except ValidationError as ve:
            logger.error(f"Validation error in AppPackageData:")
            logger.error(ve)
            for error in ve.errors():
                logger.error(f"Field: {error['loc']}, Error: {error['msg']}")
                logger.error(error)
            return
        except Exception as e:
            logger.error(f"Error running AppPackageTool: {e}")
            raise e

        storage_service._local_app_package = AppPackage(app_package)
        storage_service._update_remote_app_package()

    @staticmethod
    def upload_images() -> Dict[str, str]:
        images_dir = os.path.join(APP_PACKAGE_PATH, "images")
        if not os.path.isdir(images_dir):
            raise FileNotFoundError(f"Folder {images_dir} not found.")

        storage_service.delete_media("images")

        image_paths: Dict[str, str] = {}

        # recursively search through all folders in images_dir
        for root, dirs, files in os.walk(images_dir):
            local_path = root.replace(APP_PACKAGE_PATH, "").replace("\\", "/").lstrip("/")

            for image_name in files:
                path = os.path.join(root, image_name)
                with open(path, "rb") as f:
                    image_data = f.read()
                content_type = mimetypes.guess_type(path)[0]

                print(f"Image Name: {image_name} path: {path}  Content Type: {content_type} Local Path: {local_path}")

                url = storage_service.upload_media(local_path, image_name, content_type, None, image_data)

                image_paths[f"{local_path}/{image_name}"] = url

        return image_paths


    def process_data_list(self, data_list: List):
        for data in data_list:
            process_local_image_mixins(data, "", "")

    @staticmethod
    def pre_process_modules(modules: List[Tuple[str, Any]]):
        for module in modules:
            AppPackageTool.pre_process_module(module[0], module[1])

    @staticmethod
    def pre_process_module(module_path: str, module: Any):
        # get all attributes from data_module
        attributes = [
            attr
            for attr in dir(module)
            if not attr.startswith("__") and not callable(getattr(module, attr))
        ]

        print(f"attributes {attributes}")

        try:
            for attribute in attributes:
                process_local_image_mixins(
                    getattr(module, attribute, None), module_path, attribute
                )
        except Exception as e:
            logger.error(f"Error pre-processing images: {e}")
            raise e

    @staticmethod
    def process_modules(modules: List[Tuple[str, Any]]):
        for module in modules:
            AppPackageTool.process_module(module[0], module[1])

    @staticmethod
    def process_module(module_path: str, module: Any):
        actors = []
        scenarios = []
        lobby_tree = {}
