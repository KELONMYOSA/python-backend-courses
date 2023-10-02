from config import settings


def test_env():
    print(settings.DB_PATH)
    print(settings.MODE)

    assert settings.MODE == "TEST"
