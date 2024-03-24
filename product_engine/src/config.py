from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    origination_url: str = "http://my_api:5002"
    database_url: str = "postgresql+asyncpg://product_engine:product_engine@postgresql:5432/product_engine"


settings = Settings()
