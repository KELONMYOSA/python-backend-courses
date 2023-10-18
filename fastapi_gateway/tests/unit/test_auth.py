import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from service.utils.auth import login_user, create_access_token, authorize_user


class TestLoginUser:
    # Тест на корректные учетные данные
    def test_login_user_correct_credentials(self):
        form_data = OAuth2PasswordRequestForm(username="existing_email@example.com", password="password")
        response = login_user(form_data)
        assert "access_token" in response
        assert response["token_type"] == "bearer"

    #  Тест на неправильное имя пользователя
    def test_login_user_incorrect_username(self):
        form_data = OAuth2PasswordRequestForm(username="nonexisting_email@example.com", password="password")
        with pytest.raises(HTTPException) as exc_info:
            login_user(form_data)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == 'Incorrect username or password'

    # Тест на неправильный пароль
    def test_login_user_incorrect_password(self):
        form_data = OAuth2PasswordRequestForm(username="existing_email@example.com", password="wrong_password")
        with pytest.raises(HTTPException) as exc_info:
            login_user(form_data)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == 'Incorrect username or password'


class TestAuthorizeUser:
    # Тест на корректный токен и получение данных пользователя
    def test_authorize_user_correct_token(self):
        token = create_access_token("existing_email@example.com")
        user = authorize_user(token)
        assert user.name == "Name"
        assert user.email == "existing_email@example.com"

    # Тест на некорректный токен
    def test_authorize_user_invalid_token(self):
        token = jwt.encode({"sub": "nonexisting_email@example.com"}, "wrong_secret_key", algorithm="HS256")
        with pytest.raises(HTTPException) as exc_info:
            authorize_user(token)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == 'Could not validate credentials'
