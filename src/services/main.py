from src.settings import quiply_settings
from .storage import get_storage_service, BaseStorageService

storage_service: BaseStorageService = get_storage_service(quiply_settings.services.storage.provider)
