import os
from typing import Generic, TypeVar, List, Optional, Type

import yaml
from devtools import debug
from pydantic import BaseModel, TypeAdapter

from src.models.app_package import AppPackageData
from .constants import APP_PACKAGE_PATH
from .utils import process_local_image_mixins

T = TypeVar('T', bound=BaseModel)


class TemplateConfig(BaseModel, Generic[T]):
    root_folder: str
    attribute_name: str
    model_class: Type[T]

    def load_data_list(self) -> List[T]:
        folder = os.path.join(APP_PACKAGE_PATH, self.root_folder)

        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Directory {folder} not found")

        data_list: List[T] = []

        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.yaml'):
                    yaml_file = os.path.join(root, file)
                    data_list.append(self._load_yaml_file(yaml_file))

        return data_list

    def _load_yaml_file(self, file_path: str) -> T:
        print(f"Loading data from {file_path}")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            data = yaml.safe_load(file)

        adapted = TypeAdapter(self.model_class).validate_python(data)
        return adapted

    def process_data_list(
            self,
            app_package: AppPackageData,
            data_list: List[T],
            remote_data: Optional[AppPackageData] = None
    ) -> List[T]:
        for data in data_list:
            path = os.path.join(APP_PACKAGE_PATH, self.root_folder)
            if hasattr(data, 'uid'):
                path = os.path.join(path, data.uid)

            firebase_path = self.root_folder
            if hasattr(data, 'uid'):
                firebase_path = os.path.join(firebase_path, data.uid)

            process_local_image_mixins(app_package, data, path, firebase_path)
        return data_list

    # def load_data_list(self) -> List[T]:
    #     folder = os.path.join(APP_PACKAGE_PATH, self.root_folder)
    #     init_file = os.path.join(folder, '__init__.py')
    #     if not os.path.isfile(init_file):
    #         raise FileNotFoundError(f"__init__.py not found in {folder}")
    #
    #     # Ensure the parent directory of the module is in sys.path
    #     parent_dir = os.path.dirname(folder)
    #     if parent_dir not in sys.path:
    #         sys.path.append(parent_dir)
    #
    #     # module_name = os.path.basename(os.path.normpath(folder))
    #
    #     # Extract the full package name based on the folder structure
    #     relative_folder = os.path.relpath(folder, parent_dir)
    #     module_name = relative_folder.replace(os.path.sep, '.')
    #
    #
    #     spec = importlib.util.spec_from_file_location(module_name, init_file)
    #     if spec is None:
    #         raise ImportError(f"Could not load spec for module {module_name} from {init_file}")
    #
    #     module = importlib.util.module_from_spec(spec)
    #     module.__package__ = module_name
    #     spec.loader.exec_module(module)
    #
    #     return getattr(module, self.attribute_name, [])
    #
    # def process_data_list(
    #         self,
    #         app_package: AppPackageData,
    #         data_list: List[T],
    #         remote_data: Optional[AppPackageData] = None
    # ) -> List[T]:
    #     for data in data_list:
    #         path = APP_PACKAGE_PATH + '/' + self.root_folder
    #         if hasattr(data, 'uid'):
    #             path += '/' + data.uid
    #
    #         firebase_path = self.root_folder
    #         if hasattr(data, 'uid'):
    #             firebase_path += '/' + data.uid
    #
    #         process_local_image_mixins(app_package, data, path, firebase_path)
    #     return data_list
