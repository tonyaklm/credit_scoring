from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    scoring_url: str = "http://my_api:5003"
    database_url: str = "postgresql+asyncpg://origination:origination@postgresql:5432/origination"


settings = Settings()
