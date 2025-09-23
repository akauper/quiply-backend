from typing import Any

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth as fs_auth, firestore, storage as fs_storage

load_dotenv()

BUCKET_NAME = 'quiply-preview.appspot.com'

USERS_COLLECTION = 'users'
WAITLIST_USERS_COLLECTION = 'waitlistUsers'
APP_PACKAGE_COLLECTION = 'appPackage'

APP_PACKAGE_VERSION_DOCUMENT = APP_PACKAGE_COLLECTION + '/version'
APP_PACKAGE_DATA_DOCUMENT = APP_PACKAGE_COLLECTION + '/data'


def _init_firestore() -> tuple[Any, Any]:
    try:
        # Try to get the default app, if it has already been initialized.
        app = firebase_admin.get_app()
    except ValueError:
        # If it hasn't been initialized yet, initialize it here.
        app = firebase_admin.initialize_app()

    a = fs_auth.Client(app)
    d = firestore.client()

    # _ensure_collections_exist(d)

    return a, d


def _ensure_collections_exist(d: Any):
    def check_collection_exists(collection_name: str) -> bool:
        docs = d.collection(collection_name).limit(1).get()
        return len(list(docs)) > 0

    placeholder_data = {'placeholder': True}

    if not check_collection_exists(USERS_COLLECTION):
        d.collection(USERS_COLLECTION).document('placeholder').set(placeholder_data)

    if not check_collection_exists('waitlistUsers'):
        d.collection(WAITLIST_USERS_COLLECTION).document('placeholder').set(placeholder_data)

    if not check_collection_exists(APP_PACKAGE_COLLECTION):
        d.document(APP_PACKAGE_VERSION_DOCUMENT).set({'value': 1})
        d.document(APP_PACKAGE_DATA_DOCUMENT).set({'version': 1})


auth, db = _init_firestore()
storage = fs_storage
