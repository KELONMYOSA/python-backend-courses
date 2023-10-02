import os
import shutil

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from config import settings
from service.utils.auth import login_user


def copy_test_db_from_template():
    template_path = "database/test_db_template.sqlite"
    test_db_path = "database/test_db.sqlite"
    shutil.copy2(template_path, test_db_path)


def remove_test_db():
    os.remove("database/test_db.sqlite")


@pytest.fixture(scope="class", autouse=True)
def setup_db():
    assert settings.MODE == "TEST"
    copy_test_db_from_template()
    yield
    remove_test_db()


@pytest.fixture()
def auth_token():
    form_data = OAuth2PasswordRequestForm(username="admin@mail.ru", password="admin")
    response = login_user(form_data)

    return response["access_token"]


@pytest.fixture()
def auth_token_no_orders():
    form_data = OAuth2PasswordRequestForm(username="test@mail.ru", password="test")
    response = login_user(form_data)

    return response["access_token"]
