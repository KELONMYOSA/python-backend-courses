from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='fastapi_gateway/.env', env_file_encoding='utf-8')

    SECRET_KEY: str
    DB_PATH: str
    GO_AUTH_SERVER: str

    MODE: str


settings = Settings()
