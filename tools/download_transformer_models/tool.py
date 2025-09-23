import os
from pathlib import Path
from typing import Union

from src.utils import logger
from ..base_tool import BaseTool
from dotenv import load_dotenv


class DownloadTransformerModelsTool(BaseTool):
    def run_all(self, **kwargs) -> None:
        load_dotenv()
        token = os.getenv("HF_TOKEN")
        force = kwargs.get('force', False)

        logger.info(f"Downloading all transformer models with force={force}...")

        transformer_models_root = Path(__file__).parent.parent.parent / "transformer_models"
        model_list_path = transformer_models_root / "model_list.txt"
        download_folder = transformer_models_root / "models"

        commands = []
        models = []

        with open(model_list_path, "r") as f:
            models = f.read().splitlines()

        for model in models:
            model_download_path = model.split("/")[-1]
            if not force and os.path.isdir(download_folder / model):
                logger.info(f"Skipping model {model} because it already exists.")
                continue

            commands.append(f'git clone https://eintime64:{token}@huggingface.co/{model} {download_folder / model_download_path}')

        for command in commands:
            logger.info(f"Running command: {command}")
            os.system(command)

        logger.info(f"Finished downloading all transformer models with force={force}.")
