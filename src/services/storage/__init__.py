from .base_service import BaseStorageService
from .firestore import FirestoreStorageService


def get_storage_service(name: str) -> BaseStorageService:
    if name == "firestore":
        return FirestoreStorageService()
    else:
        raise NotImplementedError
