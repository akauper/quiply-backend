import asyncio
from datetime import datetime
from typing import Optional, TypeVar

from devtools import debug
from firebase_admin import auth
from firebase_admin.auth import UserRecord
from pydantic import BaseModel, Field

from models import AccountData, UserProfile
from models.user import UserRole
from ..base_tool import BaseTool

from firestore import db


_T = TypeVar('_T', bound=BaseModel)


class FbUserData(BaseModel):
    display_name: str
    email: str
    phone_number: Optional[str] = Field(default=None)
    password: str


class CreateUserTool(BaseTool):
    def run_all(self, **kwargs) -> None:
        self.run()

    def run(self):
        return asyncio.run(self.run_async())

    async def run_async(self) -> None:
        while True:
            print("Creating a new user in Firestore database")

            email = input("Enter user's email: ")
            password = input("Enter user's password: ")
            first_name = input("Enter user's first name: ")
            last_name = input("Enter user's last name: ")
            role = input("Is the user an investor? (yes/no): ")

            user_data = FbUserData(
                display_name=f"{first_name} {last_name}", email=email, password=password
            )

            is_investor = role.lower() == "yes"

            print("\nPlease confirm the entered data:")
            print(f"Email: {user_data.email}")
            print(f"Display Name: {user_data.display_name}")
            print(f"Phone Number: {user_data.phone_number}")
            print(f"Password: {user_data.password}")
            print(f"Is Investor: {is_investor}")

            confirmation = input("\nIs this information correct? (yes/no): ").lower()

            if confirmation == "yes":
                user_record = auth.create_user(
                    **user_data.model_dump(exclude_unset=True)
                )
                print(
                    f"User {user_record.uid} added to authentication... adding to Firestore now"
                )
                account_data = add_user_to_firestore(user_record, first_name, last_name, is_investor)
                print("User added to Firestore successfully!")
                debug(account_data)
                break
            else:
                print("Let's try again.")


def add_user_to_firestore(
    user_record: UserRecord,
        first_name: str,
        last_name: str,
        is_investor: bool = False,
) -> AccountData:
    roles = [
        UserRole.USER,
    ]
    if is_investor:
        roles.append(UserRole.INVESTOR)

    account_data = AccountData(
        id=user_record.uid,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        role=roles,
        email=user_record.email,
        first_name=first_name,
        last_name=last_name,
        profile=UserProfile(
            account_id=user_record.uid,
            name=f"{first_name} {last_name}",
        ),
    )

    USERS_COLLECTION = 'users'
    ACCOUNT_DATA_DOCUMENT_PATH = USERS_COLLECTION + '/{user_id}'

    def _create_doc(path: str, data: _T) -> _T:
        try:
            doc_ref = db.document(path)
            data_dict = data.model_dump()
            debug(data_dict)
            doc_ref.set(data_dict)
            print(f"Created {path}: {data}")
            return data
        except Exception as e:
            print(e)
            raise e

    _create_doc(ACCOUNT_DATA_DOCUMENT_PATH.format(user_id=user_record.uid), account_data)
    return account_data
