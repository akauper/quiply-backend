from typing import List

from devtools import debug
from pydantic import ValidationError

from src.models.data import AppPackage, AppPackageData
from src.models.schemas import ActorSchema, ScenarioSchema, MentorSchema
from src.services import storage_service
from src.utils import logger
from .constants import ACTOR_TEMPLATES_ROOT, SCENARIO_TEMPLATES_ROOT, ADVISOR_TEMPLATES_ROOT
from .models import TemplateConfig, TemplateFolders
from ..base_tool import BaseTool

remote_version = storage_service._fetch_remote_app_package_version()
if not remote_version:
    remote_version = 0
remote_data = storage_service._fetch_remote_app_package_data()


def get_actor_templates() -> List[ActorSchema]:
    return remote_data.actors if remote_data else []


def get_scenario_templates() -> List[ScenarioSchema]:
    return remote_data.scenarios if remote_data else []


def get_advisor_templates() -> List[MentorSchema]:
    return remote_data.advisors if remote_data else []


ACTOR_TEMPLATES = TemplateConfig(
    get_existing=get_actor_templates,
    upload_image=storage_service._upload_actor_template_image,
    upload_video=storage_service._upload_actor_template_video,
    folders=TemplateFolders(
        root=ACTOR_TEMPLATES_ROOT,
        active=f"{ACTOR_TEMPLATES_ROOT}/active",
        inactive=f"{ACTOR_TEMPLATES_ROOT}/inactive",
        images=f"{ACTOR_TEMPLATES_ROOT}/images",
        videos=f"{ACTOR_TEMPLATES_ROOT}/videos",
    )
)

SCENARIO_TEMPLATES = TemplateConfig(
    get_existing=get_scenario_templates,
    upload_image=storage_service._upload_scenario_template_image,
    upload_video=storage_service._upload_scenario_template_video,
    folders=TemplateFolders(
        root=SCENARIO_TEMPLATES_ROOT,
        active=f"{SCENARIO_TEMPLATES_ROOT}/active",
        inactive=f"{SCENARIO_TEMPLATES_ROOT}/inactive",
        images=f"{SCENARIO_TEMPLATES_ROOT}/images",
        videos=f"{SCENARIO_TEMPLATES_ROOT}/videos",
    )
)

ADVISOR_TEMPLATES = TemplateConfig(
    get_existing=get_advisor_templates,
    upload_image=storage_service._upload_advisor_template_image,
    upload_video=storage_service._upload_advisor_template_video,
    folders=TemplateFolders(
        root=ADVISOR_TEMPLATES_ROOT,
        active=f"{ADVISOR_TEMPLATES_ROOT}/active",
        inactive=f"{ADVISOR_TEMPLATES_ROOT}/inactive",
        images=f"{ADVISOR_TEMPLATES_ROOT}/images",
        videos=f"{ADVISOR_TEMPLATES_ROOT}/videos",
    )
)


class AppPackageTool(BaseTool):
    def run_all(self, **kwargs) -> None:
        force = kwargs.get('force', False)

        logger.info(f"Running Tool AppPackageTool with force={force}...")

        try:
            actors = ACTOR_TEMPLATES.load(force)
            scenarios = SCENARIO_TEMPLATES.load(force)
            advisors = []

            debug(actors)
            debug(scenarios)
            debug(advisors)


            data: AppPackageData = AppPackageData(
                version=remote_version + 1,
                actors=actors,
                scenarios=scenarios,
                advisors=advisors,
                # advisors=ADVISOR_TEMPLATES.load(force),
            )
        except ValidationError as ve:
            logger.error(f"Validation error in AppPackageData:")
            logger.error(ve)
            for error in ve.errors():
                logger.error(f"Field: {error['loc']}, Error: {error['msg']}")
                logger.error(error)
            return
        except Exception as e:
            logger.error(e)
            return

        storage_service._local_app_package = AppPackage(data)
        storage_service._update_remote_app_package()


