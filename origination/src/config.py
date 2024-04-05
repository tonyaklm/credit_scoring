from pydantic_settings import BaseSettings

my_api = ""


class Settings(BaseSettings):
    scoring_url: str = f"http://{my_api}:5003"
    product_engine_url: str = f"http://{my_api}:5001"
    database_url: str = "postgresql+asyncpg://origination:origination@postgresql:5432/origination"


settings = Settings()
