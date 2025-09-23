import mimetypes
import time
from datetime import datetime
from typing import Literal, TypeVar, Type, Dict, Optional
from uuid import uuid4

from devtools import debug
from pydantic import BaseModel

from src.models.app_package import AppPackageData

# import firebase_admin
# from firebase_admin import auth, firestore, storage
from firestore import auth, db, storage
from src.models import (
    ScenarioInstance,
    ScenarioConfig,
    ScenarioResult,
    ContextReference,
    AccountData,
)
from src.utils.logging import loggers
from ..base_service import BaseStorageService

import os

BUCKET_NAME = os.environ.get('FIREBASE_STORAGE_BUCKET', 'quiply-preview.appspot.com')

USERS_COLLECTION = "users"
SCENARIO_INSTANCE_COLLECTION_PATH = (
    USERS_COLLECTION + "/{user_id}/scenarioInstances/{scenario_instance_id}"
)
SCENARIO_RESULT_COLLECTION_PATH = (
    USERS_COLLECTION + "/{user_id}/scenarioResults/{scenario_result_id}"
)
SCENARIO_CONFIG_COLLECTION_PATH = (
    USERS_COLLECTION + "/{user_id}/scenarioConfigs/{config_name}"
)
CONTEXT_REFERENCE_COLLECTION_PATH = (
    USERS_COLLECTION + "/{user_id}/contextReferences/{context_reference_uid}"
)
ACCOUNT_DATA_DOCUMENT_PATH = USERS_COLLECTION + "/{user_id}"

APP_PACKAGE_COLLECTION = "appPackage"
APP_PACKAGE_VERSION_DOCUMENT_PATH = APP_PACKAGE_COLLECTION + "/version"
APP_PACKAGE_DATA_DOCUMENT_PATH = APP_PACKAGE_COLLECTION + "/data"

ACTOR_TEMPLATES_COLLECTION = "actorTemplates"
ADVISOR_TEMPLATES_COLLECTION = "advisorTemplates"
SCENARIO_TEMPLATES_COLLECTION = "scenarioTemplates"


def get_content_type(file_name):
    content_type, encoding = mimetypes.guess_type(file_name)
    return content_type if content_type else "text/plain"


image_mime_map = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}

_T = TypeVar("_T", bound=BaseModel)


class FirestoreStorageService(BaseStorageService):
    def __init__(self):
        self.auth = auth
        self.db = db
        self.storage = storage
        super().__init__()

    def _fetch_remote_app_package_version(self) -> int:
        try:
            doc = self.db.document(APP_PACKAGE_VERSION_DOCUMENT_PATH).get()
            return doc.to_dict().get("value", None)
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _fetch_remote_app_package_data(self) -> AppPackageData | None:
        doc = self.db.document(APP_PACKAGE_DATA_DOCUMENT_PATH).get()
        try:
            app_package = AppPackageData.model_validate(doc.to_dict())
            return app_package
        except Exception as e:
            loggers.storage.exception(e)
            debug(doc.to_dict())
            return None

    def _update_remote_app_package(self) -> None:
        try:
            doc_ref = self.db.document(APP_PACKAGE_DATA_DOCUMENT_PATH)
            local_data = self.local_app_package.data
            doc_ref.set(local_data.model_dump())
            self._update_remote_app_package_version(self.local_app_package.version)
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _update_remote_app_package_version(self, version: int) -> None:
        try:
            doc_ref = self.db.document(APP_PACKAGE_VERSION_DOCUMENT_PATH)
            doc_ref.set({"value": version})
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _delete_old_images(self, collection_name: str, uid: str) -> None:
        try:
            bucket = self.storage.bucket(BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=f"{collection_name}/{uid}/images/")
            for blob in blobs:
                blob.delete()
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _upload_image(
        self, collection_name: str, uid: str, content_type: str, image_content
    ) -> str:
        try:
            self._delete_old_images(collection_name, uid)
            bucket = self.storage.bucket(BUCKET_NAME)
            extension = (
                image_mime_map[content_type]
                if content_type in image_mime_map
                else ".jpg"
            )
            blob = bucket.blob(
                f"{collection_name}/{uid}/images/{time.time_ns()}.{extension}"
            )

            metadata = {
                "firebaseStorageDownloadTokens": uuid4(),
                "uid": uid,
                "timestamp": datetime.now().isoformat(),
            }
            blob.metadata = metadata

            cache_control = "public, max-age=0, must-revalidate"
            blob.cache_control = cache_control

            blob.upload_from_string(image_content, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _delete_old_videos(
        self, collection_name: str, uid: str, video_type: str
    ) -> None:
        try:
            bucket = self.storage.bucket(BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=f"{collection_name}/{uid}/videos/")
            for blob in blobs:
                if video_type in blob.name or video_type == "all":
                    blob.delete()
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _upload_video(
        self,
        collection_name: str,
        uid: str,
        content_type: str,
        video_type: str,
        video_content,
    ) -> str:
        try:
            self._delete_old_videos(collection_name, uid, video_type)
            bucket = self.storage.bucket(BUCKET_NAME)
            extension = ".mp4"
            blob = bucket.blob(
                f"{collection_name}/{uid}/videos/{video_type}-{time.time_ns()}.{extension}"
            )

            metadata = {
                "firebaseStorageDownloadTokens": uuid4(),
                "uid": uid,
                "timestamp": datetime.now().isoformat(),
            }
            blob.metadata = metadata

            cache_control = "public, max-age=0, must-revalidate"
            blob.cache_control = cache_control

            blob.upload_from_string(video_content, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _create_doc(self, path: str, data: _T) -> _T:
        try:
            doc_ref = self.db.document(path)
            # debug(data)
            data_dict = data.model_dump()
            debug(data_dict)
            doc_ref.set(data_dict)
            loggers.storage.info(f"Created {path}: {data}")
            return data
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _get_doc(self, path: str, model: Type[_T]) -> _T:
        try:
            doc = self.db.document(path).get()
            return model.model_validate(doc.to_dict())
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _delete_doc(self, path: str) -> None:
        loggers.storage.info(f"Deleting {path}")
        try:
            doc_ref = self.db.document(path)
            doc_ref.delete()
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _update_doc(self, path: str, data: _T) -> None:
        try:
            debug(data)
            doc_ref = self.db.document(path)
            data_dict = data.model_dump()
            debug(data_dict)
            doc_ref.set(data_dict)
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _get_blob(self, path: str):
        try:
            bucket = self.storage.bucket(BUCKET_NAME)
            blob = bucket.blob(path)
            return blob
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def delete_media(
        self,
        path: str,
        media_type: Optional[str] = None,
        *,
        metadata_selectors: Optional[Dict[str, str]] = None,
    ) -> None:
        bucket = self.storage.bucket(BUCKET_NAME)

        try:
            prefix = f"{path}/"
            if media_type:
                prefix += f"{media_type}/"
            blobs = bucket.list_blobs(prefix=prefix)
            for blob in blobs:
                if metadata_selectors:
                    # If metadata selectors are provided, check if any key-value pair matches
                    if any(
                        blob.metadata.get(key) == value
                        for key, value in metadata_selectors.items()
                    ):
                        blob.delete()
                        loggers.storage.info(f"Deleted blob {blob.name} with matching metadata from {path}/{media_type}.")
                else:
                    # If no metadata selectors, delete the blob
                    blob.delete()
                    loggers.storage.info(f"Deleted blob {blob.name} from {path}/{media_type} without metadata filtering.")

        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def upload_media(
        self,
        path: str,
        file_name: str,
        content_type: str,
        media_type: Optional[str],
        media_content
    ) -> str:
        try:
            bucket = self.storage.bucket(BUCKET_NAME)
            extension = file_name.split(".")[-1]
            if media_type:
                path += f"/{media_type}"

            blob = bucket.blob(f"{path}/{time.time_ns()}.{extension}")
            blob.content_type = content_type

            metadata = {
                "firebaseStorageDownloadTokens": uuid4(),
                "timestamp": datetime.now().isoformat(),
                "contentType": content_type,
                "fileName": file_name,
                "mediaType": media_type,
            }
            blob.metadata = metadata

            cache_control = "public, max-age=0, must-revalidate"
            blob.cache_control = cache_control

            blob.upload_from_string(media_content, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    # ------------------------------------ Actor Template ------------------------------------ #

    def _upload_actor_template_image(
        self, actor_id: str, content_type: str, image_content
    ) -> str:
        return self._upload_image(
            ACTOR_TEMPLATES_COLLECTION, actor_id, content_type, image_content
        )

    def _upload_actor_template_video(
        self, actor_id: str, content_type: str, video_type: str, video_content
    ) -> str:
        return self._upload_video(
            ACTOR_TEMPLATES_COLLECTION,
            actor_id,
            content_type,
            video_type,
            video_content,
        )

    # ------------------------------------ Advisor Template ------------------------------------ #

    def _upload_advisor_template_image(
        self, advisor_id: str, content_type: str, image_content
    ) -> str:
        return self._upload_image(
            ADVISOR_TEMPLATES_COLLECTION, advisor_id, content_type, image_content
        )

    def _upload_advisor_template_video(
        self, advisor_id: str, content_type: str, video_type: str, video_content
    ) -> str:
        return self._upload_video(
            ADVISOR_TEMPLATES_COLLECTION,
            advisor_id,
            content_type,
            video_type,
            video_content,
        )

    # ------------------------------------ Scenario Template ------------------------------------ #

    def _upload_scenario_template_image(
        self, scenario_id: str, content_type: str, image_content
    ) -> str:
        return self._upload_image(
            SCENARIO_TEMPLATES_COLLECTION, scenario_id, content_type, image_content
        )

    def _upload_scenario_template_video(
        self, scenario_id: str, content_type: str, video_type: str, video_content
    ) -> str:
        return self._upload_video(
            SCENARIO_TEMPLATES_COLLECTION,
            scenario_id,
            content_type,
            video_type,
            video_content,
        )

    # ------------------------------------ Scenario Instance ------------------------------------ #

    def _get_scenario_instance(
        self, user_id: str, scenario_instance_id: str
    ) -> ScenarioInstance:
        return self._get_doc(
            SCENARIO_INSTANCE_COLLECTION_PATH.format(
                user_id=user_id, scenario_instance_id=scenario_instance_id
            ),
            ScenarioInstance,
        )

    def _create_scenario_instance(
        self, scenario_instance: ScenarioInstance
    ) -> ScenarioInstance:
        return self._create_doc(
            SCENARIO_INSTANCE_COLLECTION_PATH.format(
                user_id=scenario_instance.account_data.id,
                scenario_instance_id=scenario_instance.uid,
            ),
            scenario_instance,
        )

    def _delete_scenario_instance(
        self, user_id: str, scenario_instance_id: str
    ) -> None:
        self._delete_doc(
            SCENARIO_INSTANCE_COLLECTION_PATH.format(
                user_id=user_id, scenario_instance_id=scenario_instance_id
            )
        )

    def _update_scenario_instance(self, scenario_instance: ScenarioInstance) -> None:
        self._update_doc(
            SCENARIO_INSTANCE_COLLECTION_PATH.format(
                user_id=scenario_instance.user_id,
                scenario_instance_id=scenario_instance.uid,
            ),
            scenario_instance,
        )

    # ------------------------------------ Scenario Result ------------------------------------ #

    def _get_scenario_result(
        self, user_id: str, scenario_result_id: str
    ) -> ScenarioResult:
        return self._get_doc(
            SCENARIO_RESULT_COLLECTION_PATH.format(
                user_id=user_id, scenario_result_id=scenario_result_id
            ),
            ScenarioResult,
        )

    def _create_scenario_result(
        self, scenario_result: ScenarioResult
    ) -> ScenarioResult:
        return self._create_doc(
            SCENARIO_RESULT_COLLECTION_PATH.format(
                user_id=scenario_result.scenario_instance.user_id,
                scenario_result_id=scenario_result.uid,
            ),
            scenario_result,
        )

    def _delete_scenario_result(self, user_id: str, scenario_result_id: str) -> None:
        self._delete_doc(
            SCENARIO_RESULT_COLLECTION_PATH.format(
                user_id=user_id, scenario_result_id=scenario_result_id
            )
        )

    def _update_scenario_result(self, scenario_result: ScenarioResult) -> None:
        self._update_doc(
            SCENARIO_RESULT_COLLECTION_PATH.format(
                user_id=scenario_result.scenario_instance.user_id,
                scenario_result_id=scenario_result.uid,
            ),
            scenario_result,
        )

    # ------------------------------------ Scenario Config ------------------------------------ #

    def _save_scenario_config(self, scenario_config: ScenarioConfig) -> None:
        self._update_doc(
            SCENARIO_CONFIG_COLLECTION_PATH.format(
                user_id=scenario_config.user_id, config_name=scenario_config.name
            ),
            scenario_config,
        )

    def _delete_scenario_config(self, user_id: str, config_name: str) -> None:
        self._delete_doc(
            SCENARIO_CONFIG_COLLECTION_PATH.format(
                user_id=user_id, config_name=config_name
            )
        )

    # ------------------------------------ Context Reference ------------------------------------ #

    def _add_context_reference(
        self,
        user_id: str,
        context_schema_uid: str,
        name: str,
        scenario_schema_id: str | None,
        reference_type: Literal["string", "file"],
        content_type: str,
        value: bytes | str,
    ) -> ContextReference:
        try:
            context_reference = ContextReference(
                user_id=user_id,
                context_template_uid=context_schema_uid,
                name=name,
                scenario_schema_id=scenario_schema_id,
                reference_type=reference_type,
                value="",
            )

            if reference_type == "file":
                blob = self._get_blob(
                    CONTEXT_REFERENCE_COLLECTION_PATH.format(
                        user_id=user_id, context_reference_uid=context_reference.uid
                    )
                )

                metadata = {
                    "firebaseStorageDownloadTokens": uuid4(),
                    "user_id": context_reference.user_id,
                    "context_template_uid": context_reference.context_template_uid,
                    "name": context_reference.name,
                    "scenario_template_id": scenario_schema_id
                    if scenario_schema_id is not None
                    else "",
                }
                blob.metadata = metadata

                blob.upload_from_string(
                    value,
                    content_type=content_type
                    if content_type
                    else get_content_type(name),
                )
                blob.make_public()
                context_reference.value = blob.public_url
            else:
                context_reference.value = value

            self._add_context_reference_entry(context_reference)
            return context_reference
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _add_context_reference_entry(self, context_reference: ContextReference):
        self._create_doc(
            CONTEXT_REFERENCE_COLLECTION_PATH.format(
                user_id=context_reference.user_id,
                context_reference_uid=context_reference.uid,
            ),
            context_reference,
        )

    def _get_context_reference(
        self, user_id: str, context_reference_uid: str
    ) -> ContextReference:
        return self._get_doc(
            CONTEXT_REFERENCE_COLLECTION_PATH.format(
                user_id=user_id, context_reference_uid=context_reference_uid
            ),
            ContextReference,
        )

    def _delete_context_reference(
        self, user_id: str, context_reference_uid: str
    ) -> None:
        try:
            loggers.storage.info(
                f"Deleting ContextReference: {context_reference_uid} for user: {user_id}"
            )
            context_reference = self.get_context_reference(
                user_id, context_reference_uid
            )
            if context_reference.reference_type == "file":
                blob = self._get_blob(
                    CONTEXT_REFERENCE_COLLECTION_PATH.format(
                        user_id=user_id, context_reference_uid=context_reference_uid
                    )
                )
                blob.delete()
            self._delete_context_reference_entry(user_id, context_reference_uid)
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _delete_context_reference_entry(
        self, user_id: str, context_reference_uid: str
    ) -> None:
        self._delete_doc(
            CONTEXT_REFERENCE_COLLECTION_PATH.format(
                user_id=user_id, context_reference_uid=context_reference_uid
            )
        )

    # ------------------------------------ User Account ------------------------------------ #

    def _create_account_data(self, account_data: AccountData) -> AccountData:
        return self._create_doc(
            ACCOUNT_DATA_DOCUMENT_PATH.format(user_id=account_data.id), account_data
        )

    def _get_account_data(self, user_id: str) -> AccountData:
        return self._get_doc(
            ACCOUNT_DATA_DOCUMENT_PATH.format(user_id=user_id), AccountData
        )

    def _delete_account_data(self, user_id: str) -> None:
        self._delete_doc(ACCOUNT_DATA_DOCUMENT_PATH.format(user_id=user_id))

    def _update_account_data(
        self, user_id: str, account_data: AccountData
    ) -> AccountData:
        self._update_doc(
            ACCOUNT_DATA_DOCUMENT_PATH.format(user_id=user_id), account_data
        )
        return account_data

    def _set_account_data_first_last_name(
        self, user_id: str, first_name: str, last_name: str
    ) -> None:
        try:
            doc_ref = self.db.collection(USERS_COLLECTION).document(user_id)
            update_dict = {}
            if first_name is not None:
                update_dict["first_name"] = first_name
            if last_name is not None:
                update_dict["last_name"] = last_name
            doc_ref.update(update_dict)
        except Exception as e:
            loggers.storage.exception(e)
            raise e

    def _upload_account_data_image(
        self, user_id: str, mime_type: str, image_content
    ) -> str:
        return self._upload_image(USERS_COLLECTION, user_id, mime_type, image_content)

    # ------------------------------------ User Profile ------------------------------------ #

    def _upload_user_profile_image(
        self, user_id: str, content_type: str, image_content
    ) -> str:
        return self._upload_image(
            USERS_COLLECTION, user_id, content_type, image_content
        )
