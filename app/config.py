import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    algorithm: str
    secret_key: str
    database_name: str
    database_port: str
    database_hostname: str
    database_password: str
    database_username: str
    access_token_expire_minutes: int
        

settings = Settings()