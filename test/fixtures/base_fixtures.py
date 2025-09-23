from unittest.mock import MagicMock

import pytest
from faker import Faker
from faker_education import SchoolProvider

from src.models import UserProfile, AccountData

fake = Faker()
fake.add_provider(SchoolProvider)


@pytest.fixture
def mock_user_profile():
    mock = MagicMock(spec=UserProfile)
    mock.name = fake.name()
    mock.image_url = fake.url()
    mock.language = fake.language_code()

    mock.gender = fake.word()
    mock.age = fake.word()
    mock.ethnicity = fake.word()
    mock.nationality = fake.word()
    mock.location = fake.word()

    mock.focus = [fake.word(), fake.word(), fake.word()]
    mock.social_comfort = fake.word()
    mock.self_confidence = fake.word()

    mock.religion = fake.word()
    mock.politics = fake.word()
    mock.occupation = fake.word()
    mock.education = fake.school_level()
    mock.income = str(fake.random_number())

    mock.body_description = fake.sentence()
    mock.face_description = fake.sentence()
    mock.hair_description = fake.sentence()
    mock.style_description = fake.sentence()

    mock.pet_preference = fake.word()
    mock.favorite_cuisine = fake.word()
    mock.vacation_destination = fake.city()
    mock.favorite_season = fake.word()
    mock.leisure_activity = fake.word()

    mock.loves = fake.sentence()
    mock.hates = fake.sentence()
    mock.hobbies = fake.sentence()

    mock.parents = fake.name()
    mock.siblings = fake.name()
    mock.spouse = fake.name()
    mock.children = fake.name()
    mock.best_friends = fake.name()

    mock.description = fake.text()

    return mock


@pytest.fixture
def mock_quiply_user(mock_user_profile):
    mock = MagicMock(spec=AccountData)

    mock.uid = fake.uuid4()
    mock.email = fake.email()
    mock.phone_number = fake.phone_number()
    mock.first_name = fake.first_name()
    mock.last_name = fake.last_name()
    mock.birthday = fake.date_of_birth()
    mock.account_image_url = fake.url()

    mock.profile = mock_user_profile

    return mock
