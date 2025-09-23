import asyncio
from abc import ABC, abstractmethod
from typing import List, Literal, Callable, Any, Dict, Optional

from src.models import (
    ActorSchema,
    MentorSchema,
    ScenarioSchema,
    ScenarioConfig,
    ContextReference,
    ScenarioInstance,
    ScenarioResult,
    UserProfile,
    AccountData,
)
from src.models.app_package import AppPackage, AppPackageData
from .cache import StorageCache
from ..base_service import BaseService
from src.settings import quiply_settings
from src.utils import logger

SCENARIO_INSTANCE_PREFIX = "scenario_instance"
SCENARIO_RESULT_PREFIX = "scenario_result"
QUIPLY_USER_PREFIX = "quiply_user"
ACCOUNT_DATA_PREFIX = "account_data"


class BaseStorageService(BaseService, ABC):
    _cache: StorageCache
    _local_app_package: AppPackage
    _remote_app_package_needs_update: bool = False

    @property
    def local_app_package(self) -> AppPackage:
        return self._local_app_package

    @property
    def _cache_enabled(self) -> bool:
        return self._config.cache.enabled

    @property
    def _cache_and_prefetch(self) -> bool:
        return self._config.cache.enabled and self._config.cache.prefetch_templates

    def __init__(self) -> None:
        super().__init__()
        self._config = quiply_settings.services.storage
        self._cache = StorageCache()
        self._local_app_package = self._get_app_package()
        # asyncio.run(self._update_app_package_loop())

    async def _update_app_package_loop(self) -> None:
        while True:
            if self._remote_app_package_needs_update:
                self._remote_app_package_needs_update = False
                self._update_remote_app_package()
            await asyncio.sleep(self._config.app_package_update_interval)

    def _get_app_package(self) -> AppPackage | None:
        remote_version = self._fetch_remote_app_package_version()
        if remote_version is None:
            raise Exception("Unable to fetch app package version")

        local_package: AppPackage = AppPackage.from_local()
        if local_package and local_package.valid and local_package.version == remote_version:
            return local_package

        remote_data = self._fetch_remote_app_package_data()
        if remote_data is None:
            logger.fatal("Unable to get remote AppPackageData. This should only occur if we are running tools.")
            return None

        local_package = AppPackage(remote_data)
        local_package.save()
        return local_package

    @abstractmethod
    def _fetch_remote_app_package_version(self) -> int:
        pass

    @abstractmethod
    def _fetch_remote_app_package_data(self) -> AppPackageData | None:
        pass

    @abstractmethod
    def _update_remote_app_package(self) -> None:
        pass

    def _get(self, uid: str, prefix: str, func: Callable[[str], Any], bypass_cache: bool) -> Any:
        key = f"{prefix}:{uid}"
        if not bypass_cache and (cached := self._cache.get(key)) is not None:
            return cached
        value = func(uid)
        self._cache.set(key, value)
        return value

    def _get_instance(self, user_id: str, uid: str, prefix: str, func: Callable[[str, str], Any], bypass_cache: bool) -> Any:
        key = f"{prefix}:{uid}"
        if not bypass_cache and (cached := self._cache.get(key)) is not None:
            return cached
        value = func(user_id, uid)
        self._cache.set(key, value)
        return value

    def _get_many(self, prefix: str, func: Callable[[], List[Any]], bypass_cache: bool) -> List[Any]:
        if not bypass_cache and (cached := self._cache.try_get_prefetch(prefix)) is not None:
            return cached
        value = func()
        self._cache.set_many({f"{prefix}:{item.id}": item for item in value})
        return value

    @abstractmethod
    def delete_media(
            self,
            path: str,
            media_type: Optional[str] = None,
            *,
            metadata_selectors: Optional[Dict[str, str]] = None,
    ) -> None:
        pass

    @abstractmethod
    def upload_media(
            self,
            path: str,
            file_name: str,
            content_type: str,
            media_type: Optional[str],
            media_content
    ) -> str:
        pass

    # ------------------------------------ Actor Template ------------------------------------ #

    def get_actor_template(self, actor_id: str) -> ActorSchema:
        return self._local_app_package.get_actor(actor_id)

    def get_actor_templates(self) -> List[ActorSchema]:
        return self._local_app_package.actors

    def update_actor_templates(self, actors: List[ActorSchema]) -> None:
        for actor in actors:
            actor.update_timestamp()
        self._local_app_package.update_actors(actors)
        self._remote_app_package_needs_update = True

    def upload_actor_template_image(self, actor_id: str, content_type: str, image_content) -> str:
        url = self._upload_actor_template_image(actor_id, content_type, image_content)
        actor = self.get_actor_template(actor_id)
        actor.image_url = url
        self.update_actor_templates([actor])
        return url

    @abstractmethod
    def _upload_actor_template_image(self, actor_id: str, content_type: str, image_content) -> str:
        pass

    def upload_actor_template_video(self, actor_id: str, content_type: str, video_type: str, video_content) -> str:
        url = self._upload_actor_template_video(actor_id, content_type, video_type, video_content)
        actor = self.get_actor_template(actor_id)
        actor.video_idle_url = url
        self.update_actor_templates([actor])
        return url

    @abstractmethod
    def _upload_actor_template_video(self, actor_id: str, content_type: str, video_type: str, video_content) -> str:
        pass

    # ------------------------------------ Advisor Template ------------------------------------ #

    def get_mentor_template(self, advisor_id: str) -> MentorSchema:
        return self._local_app_package.get_mentor(advisor_id)

    def get_advisor_templates(self) -> List[MentorSchema]:
        return self._local_app_package.advisors

    def update_advisor_templates(self, advisors: List[MentorSchema]) -> None:
        for advisor in advisors:
            advisor.update_timestamp()
        self._local_app_package.update_advisors(advisors)
        self._remote_app_package_needs_update = True

    def upload_advisor_template_image(self, advisor_id: str, content_type: str, image_content) -> str:
        url = self._upload_advisor_template_image(advisor_id, content_type, image_content)
        advisor = self.get_mentor_template(advisor_id)
        advisor.image_url = url
        self.update_advisor_templates([advisor])
        return url

    @abstractmethod
    def _upload_advisor_template_image(self, advisor_id: str, content_type: str, image_content) -> str:
        pass

    def upload_advisor_template_video(self, advisor_id: str, content_type: str, video_type: str, video_content) -> str:
        url = self._upload_advisor_template_video(advisor_id, content_type, video_type, video_content)
        advisor = self.get_mentor_template(advisor_id)
        advisor.video_idle_url = url
        self.update_advisor_templates([advisor])
        return url

    @abstractmethod
    def _upload_advisor_template_video(self, advisor_id: str, content_type: str, video_type: str, video_content) -> str:
        pass

    # ------------------------------------ Scenario Template ------------------------------------ #

    def get_scenario_schema(self, scenario_schema_id: str) -> ScenarioSchema:
        return self._local_app_package.get_scenario(scenario_schema_id)

    def get_scenario_schemas(self) -> List[ScenarioSchema]:
        return self._local_app_package.scenarios

    def update_scenario_templates(self, scenarios: List[ScenarioSchema]) -> None:
        for scenario in scenarios:
            scenario.update_timestamp()
        self._local_app_package.update_scenarios(scenarios)
        self._remote_app_package_needs_update = True

    def upload_scenario_template_image(self, scenario_id: str, content_type: str, image_content) -> str:
        url = self._upload_scenario_template_image(scenario_id, content_type, image_content)
        scenario = self.get_scenario_schema(scenario_id)
        scenario.image_url = url
        self.update_scenario_templates([scenario])
        return url

    @abstractmethod
    def _upload_scenario_template_image(self, scenario_id: str, content_type: str, image_content) -> str:
        pass

    def upload_scenario_template_video(self, scenario_id: str, content_type: str, video_type: str, video_content) -> str:
        url = self._upload_scenario_template_video(scenario_id, content_type, video_type, video_content)
        scenario = self.get_scenario_schema(scenario_id)
        scenario.video_idle_url = url
        self.update_scenario_templates([scenario])
        return url

    @abstractmethod
    def _upload_scenario_template_video(self, scenario_id: str, content_type: str, video_type: str, video_content) -> str:
        pass

    # ------------------------------------ Scenario Config ------------------------------------ #

    def save_scenario_config(self, scenario_config: ScenarioConfig) -> None:
        return self._save_scenario_config(scenario_config)

    @abstractmethod
    def _save_scenario_config(self, scenario_config: ScenarioConfig) -> None:
        pass

    def delete_scenario_config(self, user_id: str, config_name: str) -> None:
        return self._delete_scenario_config(user_id, config_name)

    @abstractmethod
    def _delete_scenario_config(self, user_id: str, config_name: str) -> None:
        pass

    # ------------------------------------ Context Reference ------------------------------------ #

    def add_context_reference(
            self,
            user_id: str,
            context_template_uid: str,
            name: str,
            scenario_schema_id: str,
            reference_type: Literal['string', 'file'],
            content_type: str,
            value: bytes | str,
    ) -> ContextReference:
        return self._add_context_reference(
            user_id,
            context_template_uid,
            name,
            scenario_schema_id,
            reference_type,
            content_type,
            value
        )

    @abstractmethod
    def _add_context_reference(
            self,
            user_id: str,
            context_schema_uid: str,
            name: str,
            scenario_schema_id: str,
            reference_type: Literal['string', 'file'],
            content_type: str,
            value: bytes | str,
    ) -> ContextReference:
        pass

    def get_context_reference(
            self,
            user_id: str,
            context_template_uid: str,
    ) -> ContextReference:
        return self._get_context_reference(
            user_id,
            context_template_uid,
        )

    @abstractmethod
    def _get_context_reference(
            self,
            user_id: str,
            context_template_uid: str,
    ) -> ContextReference:
        pass

    def delete_context_reference(
            self,
            user_id: str,
            context_reference_uid: str
    ) -> None:
        return self._delete_context_reference(
            user_id,
            context_reference_uid
        )

    @abstractmethod
    def _delete_context_reference(
            self,
            user_id: str,
            context_reference_uid: str
    ) -> None:
        pass

    # ------------------------------------ Scenario Instance ------------------------------------ #

    def get_scenario_instance(self, user_id: str, scenario_instance_id: str, bypass_cache: bool = False) -> ScenarioInstance:
        return self._get_instance(user_id, scenario_instance_id, SCENARIO_INSTANCE_PREFIX, self._get_scenario_instance, bypass_cache)

    @abstractmethod
    def _get_scenario_instance(self, user_id: str, scenario_instance_id: str) -> ScenarioInstance:
        pass

    def create_scenario_instance(self, scenario_instance: ScenarioInstance) -> ScenarioInstance:
        value = self._create_scenario_instance(scenario_instance)
        self._cache.set(f"{SCENARIO_INSTANCE_PREFIX}:{value.uid}", value)
        return value

    @abstractmethod
    def _create_scenario_instance(self, scenario_instance: ScenarioInstance) -> ScenarioInstance:
        pass

    def delete_scenario_instance(self, user_id: str, scenario_instance_id: str) -> None:
        key = f"{SCENARIO_INSTANCE_PREFIX}:{scenario_instance_id}"
        self._cache.delete(key)
        self._delete_scenario_instance(user_id, scenario_instance_id)

    @abstractmethod
    def _delete_scenario_instance(self, user_id: str, scenario_instance_id: str) -> None:
        pass

    def update_scenario_instance(self, scenario_instance: ScenarioInstance) -> None:
        scenario_instance.update_timestamp()
        self._cache.set(f"{SCENARIO_INSTANCE_PREFIX}:{scenario_instance.uid}", scenario_instance)
        self._update_scenario_instance(scenario_instance)

    @abstractmethod
    def _update_scenario_instance(self, scenario_instance: ScenarioInstance) -> None:
        pass

    # ------------------------------------ Scenario Result ------------------------------------ #

    def get_scenario_result(self, user_id: str, scenario_result_id: str, bypass_cache: bool = False) -> ScenarioResult:
        return self._get_instance(user_id, scenario_result_id, SCENARIO_RESULT_PREFIX, self._get_scenario_result, bypass_cache)

    @abstractmethod
    def _get_scenario_result(self, user_id: str, scenario_result_id: str) -> ScenarioResult:
        pass

    def create_scenario_result(self, scenario_result: ScenarioResult) -> ScenarioResult:
        value = self._create_scenario_result(scenario_result)
        self._cache.set(f"{SCENARIO_RESULT_PREFIX}:{value.uid}", value)
        return value

    @abstractmethod
    def _create_scenario_result(self, scenario_result: ScenarioResult) -> ScenarioResult:
        pass

    def delete_scenario_result(self, user_id: str, scenario_result_id: str) -> None:
        key = f"{SCENARIO_RESULT_PREFIX}:{scenario_result_id}"
        self._cache.delete(key)
        self._delete_scenario_result(user_id, scenario_result_id)

    @abstractmethod
    def _delete_scenario_result(self, user_id: str, scenario_result_id: str) -> None:
        pass

    def update_scenario_result(self, scenario_result: ScenarioResult) -> None:
        scenario_result.update_timestamp()
        self._cache.set(f"{SCENARIO_RESULT_PREFIX}:{scenario_result.uid}", scenario_result)
        self._update_scenario_result(scenario_result)

    @abstractmethod
    def _update_scenario_result(self, scenario_result: ScenarioResult) -> None:
        pass

    # ------------------------------------ User Account ------------------------------------ #

    def create_account_data(self, account_data: AccountData) -> AccountData:
        value = self._create_account_data(account_data)
        self._cache.set(f"{ACCOUNT_DATA_PREFIX}:{value.id}", value)
        return value

    @abstractmethod
    def _create_account_data(self, account_data: AccountData) -> AccountData:
        pass

    def get_account_data(self, user_id: str, bypass_cache: bool = False) -> AccountData:
        return self._get(user_id, ACCOUNT_DATA_PREFIX, self._get_account_data, bypass_cache)

    @abstractmethod
    def _get_account_data(self, user_id: str) -> AccountData:
        pass

    def delete_account_data(self, user_id: str) -> None:
        key = f"{ACCOUNT_DATA_PREFIX}:{user_id}"
        self._cache.delete(key)
        self._delete_account_data(user_id)

    @abstractmethod
    def _delete_account_data(self, user_id: str) -> None:
        pass

    def set_account_data_first_last_name(self, user_id: str, first_name: str, last_name: str) -> None:
        self._set_account_data_first_last_name(user_id, first_name, last_name)

    @abstractmethod
    def _set_account_data_first_last_name(self, user_id: str, first_name: str, last_name: str) -> None:
        pass

    def update_account_data(self, user_id: str, changed_fields: Dict[str, Any]) -> AccountData:
        account_data = self.get_account_data(user_id, True)
        for key, value in changed_fields.items():
            if hasattr(account_data, key):
                setattr(account_data, key, value)
        self._update_account_data(user_id, account_data)
        self._cache.set(f"{ACCOUNT_DATA_PREFIX}:{user_id}", account_data)
        return account_data

    @abstractmethod
    def _update_account_data(self, user_id: str, account_data: AccountData) -> AccountData:
        pass

    def upload_account_data_image(self, user_id: str, mime_type: str, image_content) -> str:
        return self._upload_account_data_image(user_id, mime_type, image_content)

    @abstractmethod
    def _upload_account_data_image(self, user_id: str, mime_type: str, image_content) -> str:
        pass

    # ------------------------------------ User Profile ------------------------------------ #

    def update_user_profile(self, uid: str, **kwargs) -> AccountData:
        account_data = self.get_account_data(uid)
        user_profile = account_data.profile
        for key, value in kwargs.items():
            if hasattr(user_profile, key) and value is not None:
                setattr(user_profile, key, value)
        account_data.profile = user_profile
        account_data.update_timestamp()
        self._cache.set(f"{ACCOUNT_DATA_PREFIX}:{account_data.id}", account_data)
        self._update_account_data(uid, account_data)
        return account_data

    def upload_user_profile_image(self, user_id: str, mime_type: str, image_content) -> str:
        return self._upload_user_profile_image(user_id, mime_type, image_content)

    @abstractmethod
    def _upload_user_profile_image(self, user_id: str, mime_type: str, image_content) -> str:
        pass

    # def create_user_account(self, quiply_user: QuiplyUser) -> QuiplyUser:
    #     value = self._create_user_account(quiply_user)
    #     self._cache.set(f"{QUIPLY_USER_PREFIX}:{value.uid}", value)
    #     return value
    #
    # @abstractmethod
    # def _create_user_account(self, quiply_user: QuiplyUser) -> QuiplyUser:
    #     pass
    #
    # def get_user_account(self, user_id: str, bypass_cache: bool = False) -> QuiplyUser:
    #     return self._get(user_id, QUIPLY_USER_PREFIX, self._get_user_account, bypass_cache)
    #
    # @abstractmethod
    # def _get_user_account(self, user_id: str) -> QuiplyUser:
    #     pass
    #
    # def delete_user_account(self, user_id: str) -> None:
    #     key = f"{QUIPLY_USER_PREFIX}:{user_id}"
    #     self._cache.delete(key)
    #     self._delete_user_account(user_id)
    #
    # @abstractmethod
    # def _delete_user_account(self, user_id: str) -> None:
    #     pass
    #
    # def set_user_account_first_last_name(self, user_id: str, first_name: str, last_name: str) -> None:
    #     self._set_user_account_first_last_name(user_id, first_name, last_name)
    #
    # @abstractmethod
    # def _set_user_account_first_last_name(self, user_id: str, first_name: str, last_name: str) -> None:
    #     pass

    # ------------------------------------ User Profile ------------------------------------ #

    # def update_user_profile(self, uid: str, **kwargs) -> QuiplyUser:
    #     quiply_user = self.get_user_account(uid)
    #     user_profile = quiply_user.profile
    #     for key, value in kwargs.items():
    #         if hasattr(user_profile, key) and value is not None:
    #             setattr(user_profile, key, value)
    #     quiply_user.profile = user_profile
    #     quiply_user.update_timestamp()
    #     self._cache.set(f"{QUIPLY_USER_PREFIX}:{quiply_user.uid}", quiply_user)
    #     self._update_user_profile(uid, user_profile)
    #     return quiply_user
    #
    # @abstractmethod
    # def _update_user_profile(self, uid: str, user_profile: UserProfile) -> QuiplyUser:
    #     pass
    #
    # def upload_user_profile_image(self, user_id: str, mime_type: str, image_content) -> str:
    #     return self._upload_user_profile_image(user_id, mime_type, image_content)
    #
    # @abstractmethod
    # def _upload_user_profile_image(self, user_id: str, mime_type: str, image_content) -> str:
    #     pass


